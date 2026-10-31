"""Offline build/package only. All generated files stay in local_only/ps3probe."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import struct
import zlib

ROOT = Path(__file__).resolve().parent
OUT = ROOT.parent / "local_only" / "ps3probe"
CONTENT = "UP0001-PS2DP0001_00-PS2DISCPROBE0001"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_icon(path):
    # Repo contains text only; generate an original simple optical-disc icon.
    pixels = bytearray()
    for y in range(320):
        pixels.append(0)
        for x in range(320):
            r2 = (x - 160) ** 2 + (y - 160) ** 2
            rgb = (185, 210, 230) if 25 ** 2 < r2 < 125 ** 2 else (20, 35, 52)
            pixels.extend(rgb + (255,))

    def chunk(name, data):
        return struct.pack(">I", len(data)) + name + data + struct.pack(">I", zlib.crc32(name + data) & 0xffffffff)

    path.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 320, 320, 8, 6, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(pixels)) + chunk(b"IEND", b""))


def main(sdk):
    sdk = Path(sdk).resolve()
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = OUT / "tmp"
    tmp.mkdir(exist_ok=True)
    env = os.environ.copy()
    env.update(PS3DK=str(sdk), PS3DEV=sdk.as_posix(), PSL1GHT=sdk.as_posix(), TEMP=str(tmp), TMP=str(tmp), PYTHONDONTWRITEBYTECODE="1")
    env["PATH"] = str(sdk / "bin") + os.pathsep + str(sdk / "ppu/bin") + os.pathsep + env["PATH"]

    def run(*args):
        subprocess.run(list(map(str, args)), cwd=OUT, env=env, check=True)

    run("cmake", "-S", ROOT, "-B", OUT / "build", "-G", "Ninja", "-DCMAKE_TOOLCHAIN_FILE=" + str(sdk / "cmake/ps3-ppu-toolchain.cmake"))
    run("cmake", "--build", OUT / "build", "--target", "PS2DiscProbe")
    stage = OUT / "stage"
    usr = stage / "USRDIR"
    usr.mkdir(parents=True, exist_ok=True)
    elf = OUT / "build/app/PS2DiscProbe.elf"
    run(sdk / "bin/make_self_npdrm.exe", elf, usr / "EBOOT.BIN", CONTENT)
    run(sdk / "bin/sfo.exe", "--title", "PS2 Disc Probe", "--appid", "PS2DP0001", "-f", sdk / "bin/sfo.xml", stage / "PARAM.SFO")
    run(sdk / "bin/sfo.exe", "validate", stage / "PARAM.SFO")
    make_icon(stage / "ICON0.PNG")
    pkg = OUT / "PS2DiscProbe.pkg"
    run(sdk / "bin/pkg.exe", "--contentid", CONTENT, str(stage) + "/", pkg)
    run(sdk / "bin/package_finalize.exe", pkg)
    from pkg_inspect import members
    files = members(pkg)
    assert set(files) == {"ICON0.PNG", "PARAM.SFO", "USRDIR/EBOOT.BIN"}, sorted(files)
    for name in ("ICON0.PNG", "PARAM.SFO"):
        assert files[name] == (stage / name).read_bytes(), name
    assert files["USRDIR/EBOOT.BIN"][:4] == b"SCE\x00"
    # SDK library/Self artifacts are our app; no Sony-derived firmware is packaged.
    manifest = dict(probe_version=3, package=pkg.name, sha256=digest(pkg), bytes=pkg.stat().st_size,
                    stages=["named-files", "aligned-storage-flags-0", "v2-baseline"],
                    storage_read_flags=[0], operation_timeout_seconds=5, stage_timeout_seconds=15,
                    absolute_timeout_seconds=60,
                    console_tested=False, installed=False, sent=False, sony_firmware_included=False,
                    sdk=str(sdk), content_id=CONTENT,
                    files=[dict(path=n, bytes=len(b), sha256=hashlib.sha256(b).hexdigest()) for n, b in sorted(files.items())])
    (OUT / "package_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (OUT / "SHA256SUMS.txt").write_text(f"{digest(pkg)}  {pkg.name}\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sdk", default="E:/tools/ps3dk/ps3-sdk-v0.26.0-windows-x86_64")
    main(parser.parse_args().sdk)
