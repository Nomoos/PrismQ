import urllib.request, json

def post(path, body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(f"http://localhost:11434{path}", data=data,
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())

d = post("/api/show", {"name": "qwen3:32b"})
info = d.get("model_info", {})

ctx = info.get("qwen3.context_length", info.get("llama.context_length", 0))
kv_heads = info.get("qwen3.attention.head_count_kv", 0)
layers = info.get("qwen3.block_count", 0)
head_dim = 128  # standard for qwen3

print(f"Context length: {ctx}")
print(f"KV heads: {kv_heads}, layers: {layers}")

if ctx and kv_heads and layers:
    # KV cache = 2 (K+V) * layers * kv_heads * head_dim * ctx * bytes_per_element
    kv_fp16 = 2 * layers * kv_heads * head_dim * ctx * 2 / 1024**3
    kv_q8   = 2 * layers * kv_heads * head_dim * ctx * 1 / 1024**3
    kv_4096 = 2 * layers * kv_heads * head_dim * 4096 * 2 / 1024**3
    weights = 18.8  # Q4_K_M on disk
    print(f"\nKV cache FP16 @ ctx={ctx}: {kv_fp16:.1f} GB  =>  total VRAM: {weights+kv_fp16:.1f} GB")
    print(f"KV cache Q8_0 @ ctx={ctx}: {kv_q8:.1f} GB   =>  total VRAM: {weights+kv_q8:.1f} GB")
    print(f"KV cache FP16 @ ctx=4096:  {kv_4096:.2f} GB  =>  total VRAM: {weights+kv_4096:.1f} GB")
    print(f"\n32b @ ctx=4096 ({weights+kv_4096:.1f} GB) + 14b (8.6 GB) = {weights+kv_4096+8.6:.1f} GB total")
    print(f"Fits in 31.8 GB: {'YES' if weights+kv_4096+8.6 < 31.8 else 'NO'}")

print("\nParameters:", d.get("parameters", "none"))
