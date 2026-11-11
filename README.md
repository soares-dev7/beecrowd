# Beecrowd — Soluções

Repositório com minhas soluções dos problemas do [Beecrowd](https://www.beecrowd.com.br/), resolvidos durante meus estudos de lógica de programação e Java.

> Meta: um exercício por dia para registrar minha evolução como desenvolvedor.

## Organização

```text
beecrowd/
├── java/
│   ├── 1001/
│   │   └── Main.java      Extremamente Básico
│   └── ...
├── python/
│   ├── 1001.py
│   └── ...
├── c/
│   └── ...
├── sql/
│   ├── 2602.sql
│   └── ...
└── novo.py                script que cria, salva e envia cada solução
```

Em Java, cada problema fica em uma pasta própria, porque a plataforma exige que a classe se chame `Main` e o Java só aceita isso quando o arquivo também se chama `Main.java`.

## Como adicionar uma solução

Precisa de [Git](https://git-scm.com/) e de [Python](https://www.python.org/) 3.8 ou mais novo. O script funciona no Windows, Linux e macOS.

```bash
# Clone (só na primeira vez)
git clone https://github.com/soares-dev7/beecrowd.git
cd beecrowd

# Uso: python novo.py <número do problema> <linguagem>
python novo.py 1001 java
python novo.py 2602 sql
python novo.py 1010 python --sem-push
```

No Linux e no macOS, se `python` não existir, use `python3`.

O script cria o arquivo na pasta certa com um modelo pronto, abre no editor, espera você colar a solução e salvar, atualiza a tabela de progresso abaixo e faz o commit e o push automaticamente. Com `--sem-push`, ele só faz o commit.

Linguagens aceitas: `java`, `python`, `c` e `sql`.

## Progresso

<!-- progresso:inicio -->
| Linguagem | Resolvidos |
|-----------|-----------|
| Java | 0 |
| Python | 0 |
| C | 0 |
| SQL | 0 |
| **Total** | **0** |
<!-- progresso:fim -->
