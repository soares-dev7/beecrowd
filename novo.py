#!/usr/bin/env python3
"""Adiciona uma solução do Beecrowd ao repositório.

Uso:
    python novo.py <numero_do_problema> <linguagem> [--sem-push]

Exemplos:
    python novo.py 1001 java
    python novo.py 2602 sql
    python novo.py 1010 python --sem-push

O que o script faz:
    1. cria o arquivo da solução na pasta da linguagem, com um modelo pronto
    2. abre o arquivo no editor padrão e espera você colar a solução
    3. avisa se o arquivo ainda estiver vazio
    4. atualiza a tabela de progresso do README
    5. faz o commit e o push

Funciona no Windows, Linux e macOS. Só precisa de Python 3.8+ e Git.
"""
import argparse
import os
import platform
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
README = RAIZ / "README.md"

# Linguagem -> (nome exibido, extensão, comentário de linha)
LINGUAGENS = {
    "java": ("Java", "java", "//"),
    "python": ("Python", "py", "#"),
    "c": ("C", "c", "//"),
    "sql": ("SQL", "sql", "--"),
}

MODELO_JAVA = """// Beecrowd #{numero} - Java
// Data: {data}
// Link: https://judge.beecrowd.com/pt/problems/view/{numero}
// A plataforma exige que a classe se chame Main.

import java.util.Scanner;

public class Main {{
    public static void main(String[] args) {{
        Scanner entrada = new Scanner(System.in);

        // cole sua solução aqui

        entrada.close();
    }}
}}
"""

MODELO_C = """// Beecrowd #{numero} - C
// Data: {data}
// Link: https://judge.beecrowd.com/pt/problems/view/{numero}

#include <stdio.h>

int main() {{
    // cole sua solução aqui

    return 0;
}}
"""

INICIO_TABELA = "<!-- progresso:inicio -->"
FIM_TABELA = "<!-- progresso:fim -->"


def caminho_da_solucao(numero: str, linguagem: str) -> Path:
    _, extensao, _ = LINGUAGENS[linguagem]
    if linguagem == "java":
        # Uma pasta por problema, porque a classe precisa se chamar Main.
        return RAIZ / "java" / numero / "Main.java"
    return RAIZ / linguagem / f"{numero}.{extensao}"


def conteudo_inicial(numero: str, linguagem: str) -> str:
    data = date.today().isoformat()
    if linguagem == "java":
        return MODELO_JAVA.format(numero=numero, data=data)
    if linguagem == "c":
        return MODELO_C.format(numero=numero, data=data)
    comentario = LINGUAGENS[linguagem][2]
    return (
        f"{comentario} Beecrowd #{numero} - {LINGUAGENS[linguagem][0]}\n"
        f"{comentario} Data: {data}\n"
        f"{comentario} Link: https://judge.beecrowd.com/pt/problems/view/{numero}\n\n"
    )


def parece_vazio(arquivo: Path, numero: str, linguagem: str) -> bool:
    """True se o arquivo continua igual ao modelo, ou ainda tem o aviso do modelo."""
    texto = arquivo.read_text(encoding="utf-8")
    if "cole sua solução aqui" in texto:
        return True
    return texto.strip() == conteudo_inicial(numero, linguagem).strip() or \
        len([l for l in texto.splitlines() if l.strip() and not l.lstrip().startswith(
            LINGUAGENS[linguagem][2])]) == 0


def abrir_no_editor(arquivo: Path) -> None:
    """Tenta abrir o arquivo; se não der, só mostra o caminho."""
    try:
        sistema = platform.system()
        if sistema == "Windows":
            os.startfile(str(arquivo))  # type: ignore[attr-defined]
        elif sistema == "Darwin":
            subprocess.run(["open", str(arquivo)], check=False)
        else:
            subprocess.run(["xdg-open", str(arquivo)], check=False,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except OSError:
        pass


def git(*args: str, capturar: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=RAIZ, check=False, text=True,
        capture_output=capturar,
    )


def contar_resolvidos() -> dict:
    contagem = {}
    for chave, (_, extensao, _) in LINGUAGENS.items():
        pasta = RAIZ / chave
        if chave == "java":
            total = len(list(pasta.glob("*/Main.java")))
        else:
            total = len(list(pasta.glob(f"*.{extensao}")))
        contagem[chave] = total
    return contagem


def atualizar_readme() -> None:
    if not README.exists():
        return
    texto = README.read_text(encoding="utf-8")
    if INICIO_TABELA not in texto or FIM_TABELA not in texto:
        return
    contagem = contar_resolvidos()
    linhas = ["| Linguagem | Resolvidos |", "|-----------|-----------|"]
    for chave, (nome, _, _) in LINGUAGENS.items():
        linhas.append(f"| {nome} | {contagem[chave]} |")
    linhas.append(f"| **Total** | **{sum(contagem.values())}** |")
    bloco = f"{INICIO_TABELA}\n" + "\n".join(linhas) + f"\n{FIM_TABELA}"
    novo = re.sub(
        re.escape(INICIO_TABELA) + r".*?" + re.escape(FIM_TABELA),
        lambda _: bloco, texto, flags=re.DOTALL,
    )
    if novo != texto:
        README.write_text(novo, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Adiciona uma solução do Beecrowd.")
    parser.add_argument("numero", help="número do problema, por exemplo 1001")
    parser.add_argument("linguagem", help="java, python, c ou sql")
    parser.add_argument("--sem-push", action="store_true",
                        help="faz o commit, mas não envia para o GitHub")
    args = parser.parse_args()

    numero = args.numero.strip()
    linguagem = args.linguagem.strip().lower()
    if not numero.isdigit():
        print(f"Número de problema inválido: {args.numero!r} (use só dígitos, ex.: 1001)")
        return 1
    if linguagem not in LINGUAGENS:
        print(f"Linguagem não suportada: {args.linguagem!r}. Use: {', '.join(LINGUAGENS)}.")
        return 1
    if git("rev-parse", "--is-inside-work-tree", capturar=True).returncode != 0:
        print("Esta pasta não é um repositório Git. Clone o repositório primeiro.")
        return 1

    arquivo = caminho_da_solucao(numero, linguagem)
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    if arquivo.exists():
        print(f"O arquivo já existe, vou usar o que está lá: {arquivo.relative_to(RAIZ)}")
    else:
        arquivo.write_text(conteudo_inicial(numero, linguagem), encoding="utf-8")
        print(f"Arquivo criado: {arquivo.relative_to(RAIZ)}")

    abrir_no_editor(arquivo)
    print("\nCole a sua solução, salve o arquivo e volte aqui.")
    try:
        input("Pressione ENTER para fazer o commit (ou Ctrl+C para cancelar)... ")
    except (KeyboardInterrupt, EOFError):
        print("\nCancelado. O arquivo continua na pasta, nada foi enviado.")
        return 1

    if parece_vazio(arquivo, numero, linguagem):
        resposta = input("O arquivo ainda parece vazio (sem a sua solução). Enviar assim mesmo? [s/N] ")
        if resposta.strip().lower() not in ("s", "sim"):
            print("Cancelado. O arquivo continua na pasta, nada foi enviado.")
            return 1

    atualizar_readme()
    caminho_relativo = arquivo.relative_to(RAIZ).as_posix()
    git("add", caminho_relativo)
    if README.exists():
        git("add", "README.md")
    if git("diff", "--cached", "--quiet").returncode == 0:
        print("Nada mudou desde o último commit, então não há o que salvar.")
        return 0

    nome = LINGUAGENS[linguagem][0]
    mensagem = f"Adiciona solução {nome} do problema {numero}"
    if git("commit", "-m", mensagem).returncode != 0:
        print("Não foi possível fazer o commit. Veja a mensagem acima.")
        return 1

    if args.sem_push:
        print("Commit feito. Use 'git push' quando quiser enviar.")
        return 0
    if git("push").returncode != 0:
        print("O commit foi feito, mas o push falhou. Tente 'git push' de novo mais tarde.")
        return 1
    print("Pronto: solução enviada para o GitHub.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
