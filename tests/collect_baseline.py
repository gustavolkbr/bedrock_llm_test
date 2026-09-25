"""
Coleta as respostas do Cosmetic Bot (via agentcore invoke) para todos os
casos do golden_dataset.json e salva em responses_baseline.json.

Uso:
    python3 tests/collect_baseline.py [--output responses_baseline.json]
    python3 tests/collect_baseline.py --ids 10,11   # reprocessa só esses casos,
                                                      # mesclando no arquivo existente

Cada caso é isolado por actor_id (definido no dataset). Casos multi-turno
usam --session-id extraído da primeira resposta para continuar a mesma
conversa no segundo turno.
"""
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional, Tuple

ROOT = Path(__file__).parent.parent
DATASET_PATH = ROOT / "golden_dataset.json"


def invoke(prompt: str, actor_id: str, session_id: Optional[str] = None) -> Tuple[str, Optional[str]]:
    """Chama `agentcore invoke` e retorna (texto_da_resposta, session_id)."""
    cmd = ["agentcore", "invoke", prompt, "--harness", "MyHarness", "--actor-id", actor_id]
    if session_id:
        cmd += ["--session-id", session_id]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        raise RuntimeError(f"agentcore invoke falhou: {result.stderr}")

    raw = result.stdout.strip()

    # A resposta vem antes da linha "Session: <uuid>"
    match = re.search(r"\nSession:\s*([a-f0-9-]+)", raw)
    session = match.group(1) if match else None
    resposta = raw.split("\nSession:")[0].strip() if "\nSession:" in raw else raw

    return resposta, session


def main():
    output_path = ROOT / "responses_baseline.json"
    ids_filtro = None

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--output":
            output_path = ROOT / args[i + 1]
            i += 2
        elif args[i] == "--ids":
            ids_filtro = {int(x) for x in args[i + 1].split(",")}
            i += 2
        else:
            i += 1

    dataset = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
    if ids_filtro is not None:
        dataset = [c for c in dataset if c["id"] in ids_filtro]

    novos_resultados = {}

    for caso in dataset:
        print(f"[{caso['id']:02d}] {caso['categoria']} — coletando...", flush=True)
        actor_id = caso["actor_id"]
        turnos = caso["turnos"]
        respostas_turnos = []
        session_id = None

        for idx, prompt in enumerate(turnos):
            try:
                resposta, session_id = invoke(prompt, actor_id, session_id)
            except Exception as e:
                resposta = f"[ERRO NA CHAMADA: {e}]"
            respostas_turnos.append({"turno": idx + 1, "prompt": prompt, "resposta": resposta})
            time.sleep(4)  # respiro entre chamadas (aumentado de 1s para 4s)

        novos_resultados[caso["id"]] = {
            "id": caso["id"],
            "categoria": caso["categoria"],
            "actor_id": actor_id,
            "turnos_completos": respostas_turnos,
            "resposta_final": respostas_turnos[-1]["resposta"],
        }
        print(f"      ok — {len(respostas_turnos[-1]['resposta'])} chars", flush=True)

    # Mescla com resultados existentes, se houver (permite reprocessar só alguns ids)
    if output_path.exists():
        existentes = {r["id"]: r for r in json.loads(output_path.read_text(encoding="utf-8"))}
    else:
        existentes = {}

    existentes.update(novos_resultados)
    resultados_final = [existentes[k] for k in sorted(existentes.keys())]

    output_path.write_text(json.dumps(resultados_final, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n{len(novos_resultados)} caso(s) atualizado(s), {len(resultados_final)} no total, salvos em {output_path}")


if __name__ == "__main__":
    main()
