"""Targeted HBC96 patches for the existing Compact80 package."""
import io
import struct
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'hermes-dec/src'))
from hermes_dec.parsers.hbc_file_parser import HBCReader
from hermes_dec.parsers.hbc_opcodes import hbc95

OPS = {i.name: i for i in hbc95._instructions}

def ins(name, *args):
    op = OPS[name]
    assert len(args) == len(op.operands), name
    values = op.structure()
    for n, v in enumerate(args, 1):
        setattr(values, f'arg{n}', v)
    return bytes([op.opcode]) + bytes(values)

def patch_player(b, sidebar=True):
    r = HBCReader()
    r.read_whole_file(io.BytesIO(b))
    changes = []

    def replace(fid, relative, expected, replacement):
        h = r.function_headers[fid]
        pos = h.offset + relative
        assert len(expected) == len(replacement)
        assert b[pos:pos+len(expected)] == expected, (fid, relative)
        b[pos:pos+len(expected)] = replacement
        changes.append((fid, relative, len(replacement)))

    # Visual expansion only: do not force global keyboard/gamepad adjustment mode.
    replace(17171, 0x245, ins('Mov', 9, 8), ins('LoadConstUInt8', 9, 1))
    replace(17200, 0x16b, ins('LoadFromEnvironment', 10, 14, 6),
            ins('LoadConstTrue', 10) * 2)
    replace(17200, 0x176, ins('LoadFromEnvironment', 10, 14, 7),
            ins('LoadConstZero', 10) * 2)
    # No opacity/translation animations for an always-visible control.
    for fid in (17175, 5966):  # slider animation effect; optional Sentry setup
        h = r.function_headers[fid]
        assert not h.hasExceptionHandler and not h.hasDebugInfo
        assert sum(x.offset == h.offset for x in r.function_headers) == 1
        b[h.offset:h.offset+4] = ins('LoadConstUndefined', 0) + ins('Ret', 0)
        Header = r.get_small_func_header_reader()
        header_pos = 128 + fid * 16
        header = Header.from_buffer_copy(b[header_pos:header_pos+16])
        assert not header.overflowed
        header.bytecodeSizeInBytes = 4
        b[header_pos:header_pos+16] = bytes(header)
        changes.append((fid, 0, 4))
    # Decorative equalizer no longer runs an 8 Hz React state timer.
    # Keep playback-state colour, change only the animation predicate.
    replace(17286, 0x37, ins('Mov', 1, 6), ins('LoadConstUInt8', 1, 0))
    # Evict inactive query results after one minute instead of five.
    replace(11293, 0x42, ins('LoadConstInt', 5, 300000), ins('LoadConstInt', 5, 60000))
    if not sidebar:
        return changes

    # Sidebar gets the SAME VolumeSlider component, outside native focus clipping.
    # Rotate its wrapper for a vertical control; native hit testing maps local X.
    fid = 17488
    h = r.function_headers[fid]
    assert not h.overflowed and not h.hasExceptionHandler and not h.hasDebugInfo
    code = bytearray(b[h.offset:h.offset+h.bytecodeSizeInBytes])
    assert code[0x2f6:0x2fa] == ins('NewArray', 7, 3)
    e = bytearray()
    def emit(name, *args): e.extend(ins(name, *args))
    def prop(obj, value, key): emit('PutNewOwnById', obj, value, r.strings.index(key))
    def string(reg, value): emit('LoadConstString', reg, r.strings.index(value))
    def require(reg, module):
        emit('LoadConstInt', reg, module)
        emit('Call2', reg, 10, 3, reg)
    emit('GetGlobalObject', 9)
    emit('GetById', 10, 9, 28, r.strings.index('__r'))
    require(11, 1890)
    emit('GetById', 11, 11, 29, r.strings.index('VolumeSlider'))
    require(12, 1)
    emit('GetByIdShort', 12, 12, 30, r.strings.index('View'))
    require(13, 224)
    emit('GetByIdShort', 14, 13, 31, r.strings.index('jsx'))
    emit('NewObject', 15)
    emit('Call3', 16, 14, 3, 11, 15)
    require(18, 1057)
    emit('GetByIdShort', 18, 18, 32, r.strings.index('size'))
    emit('NewObject', 17)
    string(19, 'absolute'); prop(17, 19, 'position')
    for key, value in [('width',164), ('height',73), ('left',-58), ('bottom',140)]:
        emit('LoadConstInt', 19, value)
        emit('Call2', 19, 18, 3, 19)
        prop(17, 19, key)
    emit('NewObject', 20)
    string(19, '-90deg'); prop(20, 19, 'rotate')
    emit('NewArray', 19, 1)
    emit('PutOwnByIndex', 19, 20, 0)
    prop(17, 19, 'transform')
    emit('LoadConstInt', 19, 1001); prop(17, 19, 'zIndex')
    emit('NewObject', 15)
    prop(15, 17, 'style'); prop(15, 16, 'children')
    emit('Call3', 16, 14, 3, 12, 15)
    emit('NewArray', 7, 2)
    emit('PutOwnByIndex', 7, 4, 0)
    emit('PutOwnByIndex', 7, 16, 1)
    # Insert after all branches, so existing relative jump destinations are stable.
    assert code[0x3be:0x3c2] == ins('PutNewOwnByIdShort', 0, 4, 81)
    code[0x3be:0x3c2] = ins('PutNewOwnByIdShort', 0, 7, 81)
    code[0x3be:0x3be] = e
    # Relocate just this function to space before the footer, retaining function ID.
    header_pos = 128 + fid * 16
    Header = r.get_small_func_header_reader()
    header = Header.from_buffer_copy(b[header_pos:header_pos+16])
    assert header.offset == h.offset
    header.offset = len(b) - 20
    header.bytecodeSizeInBytes = len(code)
    header.highestReadCacheIndex = 32
    b[-20:-20] = code
    b[header_pos:header_pos+16] = bytes(header)
    struct.pack_into('<I', b, 32, len(b))
    changes.append((fid, 'relocated', len(code)))
    return changes
