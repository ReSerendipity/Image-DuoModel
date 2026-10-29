"""
scripts/verify_watermark.py — 输出数字水印溯源验证（PRD §8.6 / §10.5 STEP 6）

用法:
    python scripts/verify_watermark.py outputs/xxx.png            # PNG 需 pillow
    python scripts/verify_watermark.py path/to/array.npy          # numpy 数组
    python scripts/verify_watermark.py -p product_id 图像路径     # 校验指定 product_id

判断口径（2026-10-29 起）:
    配置了签名密钥（IMAGE_MULTIMODEL_WATERMARK_KEY 或项目根 .watermark_key）时，
    本脚本按 HMAC 签名判定：签名无效即失败，product_id 相符也不算通过；
    未配置密钥时只能做弱校验（比对 product_id），输出里会明确标注。

提取的 payload 格式: {product_id}|{task_id}|{timestamp}（签名版在末尾再加 |{hmac-sha256 hex}）
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.integrated_app import watermark  # noqa: E402

# Windows 控制台默认 GBK 无法编码 ✅/❌ → 强制 UTF-8 输出
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def load_array(path: str) -> np.ndarray:
    p = Path(path)
    if p.suffix.lower() in (".npy",):
        return np.load(p)
    if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".bmp", ".webp"):
        try:
            from PIL import Image  # pillow
        except ImportError as e:
            raise SystemExit("需安装 pillow 才能读取图片: pip install Pillow") from e
        img = Image.open(p).convert("RGB")
        return np.asarray(img, dtype=np.float64)
    raise SystemExit(f"不支持的输入格式: {p.suffix}")


def decode_payload(bits: list[int]) -> str:
    out = bytearray()
    for i in range(0, len(bits) - 7, 8):
        byte = 0
        for j in range(8):
            byte = (byte << 1) | bits[i + j]
        out.append(byte)
    return out.decode("utf-8", errors="replace").rstrip("\x00")


def parse_signed(payload: str) -> tuple[str, str, str, str] | None:
    """从解码串里切出 `pid|task|ts|<64 hex 签名>`。

    多读的比特在载荷末尾解成噪声，所以签名段必须按格式精确切 64 位 hex，
    不能拿整串的末 64 字符去验（那样多读一位就永远验不过）。
    """
    m = re.match(r"^(?P<pid>[^|]+)\|(?P<task>[^|]+)\|(?P<ts>-?\d+)\|(?P<sig>[0-9a-fA-F]{64})", payload)
    if not m:
        return None
    return m.group("pid"), m.group("task"), m.group("ts"), m.group("sig")


def main() -> int:
    ap = argparse.ArgumentParser(description="验证 Image MultiModel 输出数字水印")
    ap.add_argument("image", help="图片/数组路径")
    ap.add_argument("-p", "--product-id", default="img_multimodel", help="期望的 product_id")
    ap.add_argument(
        "-n",
        "--n-bits",
        type=int,
        default=0,
        help="尝试提取的比特数（默认：配置了签名密钥时 1024，否则 400；配了密钥时至少按 1024 取，"
        "否则读不全 400bit 载荷 + 512bit 签名）",
    )
    args = ap.parse_args()

    has_key = watermark.has_secret_key()
    n_bits = args.n_bits or (1024 if has_key else 400)
    if has_key:
        n_bits = max(n_bits, 1024)
    arr = load_array(args.image)
    bits = watermark.extract_watermark(arr, n_bits)
    payload = decode_payload(bits)

    print("=== 水印溯源验证 ===")
    print(f"输入     : {args.image}")
    print(f"载荷     : {payload}")

    signed = parse_signed(payload) if has_key else None
    if signed:
        pid, task_id, ts, sig = signed
        sig_ok = watermark.verify_extracted(f"{pid}|{task_id}|{ts}|{sig}") is not None
        print(f"product_id: {pid}")
        print(f"task_id   : {task_id}")
        print(f"timestamp : {ts}")
        print("签名     : ✅ HMAC 校验通过" if sig_ok else "签名     : ❌ 载荷被改动，或不是本机密钥签发的")
        ok = sig_ok and pid == args.product_id
        print("校验     : ✅ 签名有效且匹配 product_id" if ok else "校验     : ❌ 未通过（签名或 product_id 不符）")
        return 0 if ok else 1

    if has_key:
        print("签名     : ❌ 未从载荷中解析出签名段（可能未签名、载荷被截断或图像被重编码）")
        return 1

    if "|" in payload:
        pid, task_id, ts = payload.split("|", 2)
        print(f"product_id: {pid}")
        print(f"task_id   : {task_id}")
        print(f"timestamp : {ts}")
        print("签名     : ⚠ 未配置签名密钥 ⇒ 只能做弱校验，无法证伪归属")
        ok = pid == args.product_id
        print("校验     : ✅ 匹配 product_id（弱校验）" if ok else "校验     : ❌ product_id 不匹配")
        return 0 if ok else 1
    print("校验     : ❌ 未提取到有效载荷")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
