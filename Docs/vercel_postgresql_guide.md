# 📄 Guia: Configurando PostgreSQL do Vercel com Django

Este guia detalha os passos necessários para configurar e utilizar o serviço de banco de dados PostgreSQL oferecido pelo Vercel com uma aplicação backend Django, como a utilizada neste projeto.

**Pré-requisitos:**

*   Sua aplicação Django está configurada para usar PostgreSQL (localmente ou com variáveis de ambiente).
*   Você tem uma conta no Vercel e o projeto importado.

---

## Passos para Configuração

1.  **Crie um Projeto no Vercel (se necessário):**
    *   Importe seu repositório Git (GitHub, GitLab, Bitbucket) para o Vercel.

2.  **Adicione um Banco de Dados PostgreSQL no Vercel:**
    *   No painel do seu projeto Vercel, navegue até a seção **Storage** ou **Databases**.
    *   Clique em **Create New** e selecione **PostgreSQL**.
    *   Siga as instruções na tela para configurar as opções do banco de dados e finalize a criação.

3.  **Obtenha as Credenciais de Conexão:**
    *   Após a criação, o Vercel exibirá os detalhes de conexão do seu banco de dados PostgreSQL.
    *   Copie a **Connection String (URL)** completa ou os detalhes separados (Host, Database, User, Password, Port).
    *   **Mantenha essas credenciais seguras e não as compartilhe publicamente.**

4.  **Configure Variáveis de Ambiente no Vercel:**
    *   No painel do projeto Vercel, vá para **Settings** > **Environment Variables**.
    *   Adicione as credenciais do banco de dados como variáveis de ambiente. Recomenda-se usar nomes claros, como:
        *   `DATABASE_URL` (para a connection string completa)
        *   Ou variáveis separadas: `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`.
    *   Defina essas variáveis para os ambientes **Production**, **Preview** e **Development** (conforme necessário).
    *   Adicione também outras variáveis de ambiente que seu Django precise, como `SECRET_KEY`.

5.  **Atualize as Configurações do Django (`settings.py`):**
    *   No seu arquivo `gateway_service/backend/settings.py`, modifique a configuração `DATABASES` para ler as informações de conexão das variáveis de ambiente configuradas no Vercel.
    *   É altamente recomendável usar uma biblioteca como `dj-database-url` para parsear a `DATABASE_URL` ou configurar o dicionário `DATABASES` a partir de variáveis separadas.
    *   **Exemplo usando `dj-database-url` (requer `pip install dj-database-url` e adicionar ao `requirements.txt`):**

    ```python
    import os
    import dj_database_url

    # ... outras configurações ...

    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600 # Opcional: configura tempo de vida da conexão
        )
    }

    # ... outras configurações ...
    ```

    *   **Exemplo usando variáveis separadas (requer ler `os.environ` diretamente):**

    ```python
    import os

    # ... outras configurações ...

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME'),
            'USER': os.environ.get('DB_USER'),
            'PASSWORD': os.environ.get('DB_PASSWORD'),
            'HOST': os.environ.get('DB_HOST'),
            'PORT': os.environ.get('DB_PORT'),
        }
    }

    # ... outras configurações ...
    ```

6.  **Execute as Migrações do Django no Vercel:**
    *   Após o deploy inicial e a configuração das variáveis de ambiente, você precisará executar os comandos de migração do Django (`python manage.py migrate`) no ambiente do Vercel para criar as tabelas no seu banco de dados PostgreSQL.
    *   A forma de fazer isso depende da sua configuração de deploy no Vercel. Opções comuns incluem:
        *   Adicionar `python manage.py migrate` ao seu **Build Command** ou **Install Command** no Vercel (se for seguro rodar a cada build).
        *   Criar uma Serverless Function separada no Vercel que execute as migrações quando acionada (mais seguro para produção).
        *   Usar a Vercel CLI para executar o comando remotamente após o deploy.
    *   Consulte a documentação oficial do Vercel sobre como executar comandos pós-deploy ou tarefas de gerenciamento.

7.  **Configure o `vercel.json` para o Backend (se necessário):**
    *   Certifique-se de que seu arquivo `vercel.json` na raiz do projeto (ou na pasta do backend) esteja configurado corretamente para construir e implantar seu backend Django como Serverless Functions, definindo as `builds` e `routes` apropriadas para direcionar o tráfego da API para o seu backend Python.

---

Após seguir estes passos, sua aplicação Django implantada no Vercel deverá ser capaz de se conectar e utilizar o banco de dados PostgreSQL do Vercel.
