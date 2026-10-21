# libraille-backend
API REST em FastAPI para transliteração Braille Grau 1 e gestão de conteúdos.

```
libraille-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                     # Inicialização do FastAPI e inclusão das rotas
│   │
│   ├── core/                       # Configurações globais e regras centrais do sistema
│   │   ├── __init__.py
│   │   ├── config.py               # Leitura de variáveis do .env (Pydantic Settings)
│   │   ├── security.py             # Criptografia de senhas (bcrypt) e tokens JWT
│   │   └── braille_translator.py   # O motor de conversão pura (texto -> bytes 0..63)
│   │
│   ├── db/                         # Configuração e sessão do banco de dados MySQL
│   │   ├── __init__.py
│   │   ├── session.py              # Engine do SQLAlchemy e SessionLocal
│   │   └── base.py                 # Importa todos os models para criar as tabelas
│   │
│   ├── models/                     # Tabelas do banco de dados (ORM - SQLAlchemy)
│   │   ├── __init__.py
│   │   ├── user.py                 # Tabela de usuários (id, nome, email, senha)
│   │   ├── book.py                 # Tabela de livros/textos (id, titulo, conteudo, user_id)
│   │   └── progress.py             # Histórico (qual byte/caractere a pessoa parou de ler)
│   │
│   ├── schemas/                    # Validação de dados de entrada e saída (Pydantic)
│   │   ├── __init__.py
│   │   ├── user_schema.py          # Schemas: UserCreate, UserLogin, UserResponse
│   │   ├── book_schema.py          # Schemas: BookUpload, BookResponse
│   │   └── braille_schema.py       # Schemas: BrailleTranslateRequest, BrailleResponse
│   │
│   ├── services/                   # Regras de negócio e utilitários pesados
│   │   ├── __init__.py
│   │   ├── file_service.py         # Leitura e sanitização de arquivos .txt e .epub
│   │   └── serial_service.py       # Conexão USB/Serial direta com ESP32 (se aplicável)
│   │
│   └── routers/                    # Endpoints da API divididos por assunto
│       ├── __init__.py
│       ├── auth_routes.py          # POST /auth/register, POST /auth/login
│       ├── book_routes.py          # POST /books/upload, GET /books, GET /books/{id}
│       └── translate_routes.py     # POST /translate/text, POST /translate/file
│
├── tests/                          # Bateria de testes automatizados com pytest
│   ├── __init__.py
│   ├── test_translator.py          # Testes unitários do motor Braille
│   ├── test_file_service.py        # Testes de upload/leitura de TXT e EPUB
│   └── test_auth.py                # Testes de login e criação de conta
│
├── sample_texts/                   # Amostras reais de textos para testes rápidos
│   ├── pequeno_principe.txt
│   └── capitulo_exemplo.epub
│
├── .env.example                    # Modelo de configuração para o time copiar
├── requirements.txt                # Dependências do Python
├── .gitignore
└── README.md
```

## O que faz cada pasta e arquivo (sem jargão técnico)
Imagine o backend como um restaurante:

Dentro de `app/` (O restaurante em funcionamento)
`main.py` (O interruptor geral): É o ponto de partida. Quando você digita o comando para rodar a aplicação, é ele quem acende as luzes, liga o servidor FastAPI e avisa que o sistema está pronto para receber pedidos.

`routers/` (Os garçons / Balcão de atendimento): Onde ficam as portas de entrada da API. Quando o site em React pede "Traduza esse texto", o pedido chega no garçom de tradução (`translate_routes.py`). Quando alguém clica em "Entrar", o pedido chega no garçom de login (`auth_routes.py`).

`schemas/` (O conferente / Segurança): Antes de entregar um pedido para a cozinha, alguém precisa checar se ele veio certo. O schema confere: "O usuário digitou um e-mail válido? A senha tem mais de 6 caracteres? O texto a ser traduzido não veio em branco?". Se algo estiver errado, ele devolve o erro na hora.

`services/` (Os ajudantes de cozinha): Fazem o trabalho braçal pesado. Aqui fica o arquivo que pega um arquivo .txt ou .epub enviado pelo usuário, remove códigos desnecessários e prepara o texto limpo.

`core/` (O chef principal): Guarda as receitas secretas e exclusivas do projeto. É aqui que fica o `braille_translator.py`: o algoritmo que lê as letras em português e calcula exatamente os números de 0 a 63 para mover os pinos braille.

`models/` (As fichas de cadastro do depósito): Descreve como as coisas são anotadas no banco de dados. Exemplo: diz que a ficha do "Usuário" tem nome, e-mail e senha; e a ficha do "Livro" tem título e conteúdo.

`db/` (A chave do depósito): Configura a ponte entre o Python e o banco MySQL. Guarda o endereço de onde o banco está instalado e como abrir a conexão com segurança.

## Fora de `app/` (Ferramentas de apoio):

`sample_texts/` (A despensa de testes): Uma pasta para deixar arquivos de texto prontos (como um capítulo de Dom Casmurro ou frases de teste em .txt) para a equipe testar a tradução sem precisar ficar digitando texto na hora.

`tests/` (O controle de qualidade): Onde ficam os testes automáticos. Um script que testa o tradutor sozinho: ele manda a palavra "oi" e verifica no silêncio se o código devolveu os pontos certos de Braille.

`requirements.txt` (A lista de compras do projeto): Uma lista simples com os nomes dos programas que o Python precisa baixar pela internet para o projeto funcionar (FastAPI, Uvicorn, etc.).

`.env.example` (O formulário em branco): Um arquivo de texto que mostra quais senhas o sistema precisa para funcionar (como a senha do banco MySQL), sem colocar as senhas reais no GitHub.

`.gitignore` (A lixeira invisível): Uma lista que diz ao Git: "ignore pastas temporárias do computador e nunca mande arquivos pesados ou com senhas para a internet".

`README.md` (O manual na porta da frente): O texto que aparece na primeira página do GitHub ensinando qualquer pessoa a instalar e rodar o projeto.