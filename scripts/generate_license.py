import argparse
import hashlib
import hmac
import uuid
from datetime import datetime
from pathlib import Path

LICENSE_SECRET="".join(["AIM","-","SECRET","-","KEY","-","2026"])

def generate_license_key(license_type="pro", expire_days=None):
    uid = str(uuid.uuid4())[:4]
    # Key格式: AIM-{天数或PERM}-{签名}
    if expire_days:
        info = f"{license_type}:{expire_days}:{uid}"
        days_str = f"{expire_days:04d}"
    else:
        info = f"{license_type}:perm:{uid}"
        days_str = "PERM"
    sig = hmac.new(LICENSE_SECRET.encode(), info.encode(), hashlib.sha256).hexdigest()[:16]
    key = f"AIM-{days_str}-{sig}"
    expire_desc = f"{expire_days}天" if expire_days else "永久"
    return {"key": key, "type": license_type, "expire_days": expire_days, "expire_desc": expire_desc}

def batch_generate(license_type, count, expire_days=None):
    return [generate_license_key(license_type, expire_days) for _ in range(count)]

def save_keys(keys, output_file=None):
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"licenses_{timestamp}_{len(keys)}个.txt"
    output_path = Path("scripts") / output_file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write("AI模型API余额监控 - License Keys\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"生成数量: {len(keys)} 个\n")
        f.write("=" * 60 + "\n\n")
        for i, k in enumerate(keys, 1):
            f.write(f"[{i}] {k['key']}\n")
            f.write(f"    类型: {k['type']}\n")
            f.write(f"    有效期: {k['expire_desc']} (从激活日开始)\n\n")
        f.write("=" * 60 + "\n")
    return output_path

def main():
    parser = argparse.ArgumentParser(description="生成 License Key")
    parser.add_argument("--type", default="pro")
    parser.add_argument("--count", type=int, default=1)
    parser.add_argument("--expire", type=int, default=None, help="有效天数")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
    print(f"\n正在生成 License Key...")
    print(f"类型: {args.type}")
    print(f"数量: {args.count}")
    print(f"有效期: {args.expire or '永久'}\n")
    keys = batch_generate(args.type, args.count, args.expire)
    output_path = save_keys(keys, args.output)
    print(f"已保存到: {output_path}\n")
    print("=" * 60)
    for i, k in enumerate(keys, 1):
        print(f"[{i}] {k['key']}  ({k['expire_desc']})")
    print("=" * 60)
    print(f"\n共生成 {len(keys)} 个 License Key")

if __name__ == "__main__":
    main()
