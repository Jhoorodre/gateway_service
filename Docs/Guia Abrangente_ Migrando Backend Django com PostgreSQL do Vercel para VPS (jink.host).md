# 🚀 Guia Abrangente: Migrando Backend Django com PostgreSQL do Vercel para VPS (jink.host)

**Por Manus AI**

Este guia detalhado foi elaborado para auxiliar desenvolvedores na transição de um backend Django, que atualmente utiliza o PostgreSQL no ambiente Vercel, para uma solução de hospedagem mais controlada e flexível em uma Virtual Private Server (VPS) da jink.host. A migração para uma VPS oferece maior autonomia sobre o ambiente de servidor, permitindo configurações personalizadas, otimizações de desempenho e, em muitos casos, uma redução de custos a longo prazo para projetos com requisitos específicos ou tráfego crescente. Abordaremos desde o planejamento da arquitetura do servidor até a configuração do banco de dados PostgreSQL e o deploy da aplicação Django, garantindo uma transição suave e eficiente.

---

## 💡 Parte 1: Planejamento da Arquitetura na VPS

A escolha da arquitetura do servidor é um passo fundamental para garantir a estabilidade, segurança e desempenho da sua aplicação Django em uma VPS. Diferente do ambiente gerenciado do Vercel, onde muitos detalhes de infraestrutura são abstraídos, em uma VPS você terá controle total sobre cada componente. Esta seção descreve os principais elementos da arquitetura que serão implementados na VPS da jink.host.

### 1.1 Escolha do Sistema Operacional

Para a hospedagem de aplicações web Python/Django, as distribuições Linux baseadas em Debian ou Ubuntu são as mais recomendadas devido à sua vasta documentação, grande comunidade de suporte e facilidade de uso. Optaremos pelo **Ubuntu Server LTS (Long Term Support)**, que oferece estabilidade e atualizações de segurança por um longo período, sendo ideal para ambientes de produção.

### 1.2 Componentes da Arquitetura

A arquitetura proposta para o backend Django com PostgreSQL na VPS incluirá os seguintes componentes:

*   **Sistema Operacional**: Ubuntu Server LTS.
*   **Servidor Web (Reverse Proxy)**: Nginx.
    *   O Nginx atuará como um proxy reverso, recebendo as requisições HTTP/HTTPS dos clientes e as encaminhando para o servidor de aplicação (Gunicorn). Ele também será responsável por servir arquivos estáticos (CSS, JavaScript, imagens) de forma eficiente e gerenciar certificados SSL para HTTPS.
*   **Servidor de Aplicação WSGI**: Gunicorn.
    *   O Gunicorn (Green Unicorn) é um servidor WSGI (Web Server Gateway Interface) Python que será utilizado para servir a aplicação Django. Ele se comunicará com o Nginx e executará o código Python do seu projeto.
*   **Banco de Dados**: PostgreSQL.
    *   O PostgreSQL será instalado diretamente na VPS, oferecendo controle total sobre o banco de dados e eliminando a dependência de serviços de banco de dados externos como o Vercel Postgres. Isso permite otimizações específicas e maior segurança dos dados.
*   **Gerenciador de Processos**: systemd.
    *   Utilizaremos o `systemd` para gerenciar os processos do Gunicorn e do Nginx, garantindo que eles iniciem automaticamente com o servidor e sejam reiniciados em caso de falha.
*   **Ferramenta de Gerenciamento de Ambiente Python**: virtualenv ou venv.
    *   É crucial isolar as dependências do projeto Django em um ambiente virtual Python para evitar conflitos com outras bibliotecas do sistema e garantir a portabilidade.
*   **Firewall**: UFW (Uncomplicated Firewall).
    *   O UFW será configurado para permitir apenas o tráfego essencial (SSH, HTTP, HTTPS) e bloquear portas não utilizadas, aumentando a segurança do servidor.
*   **Ferramenta de Controle de Versão**: Git.
    *   O Git será usado para clonar o repositório do seu projeto Django para a VPS e para facilitar futuras atualizações.

### 1.3 Diagrama da Arquitetura

```mermaid
graph TD
    A[Cliente Web] --> B[Nginx (Reverse Proxy)]
    B --> C[Gunicorn (Servidor WSGI)]
    C --> D[Aplicação Django]
    D --> E[PostgreSQL (Banco de Dados)]
    B -- Serve arquivos estáticos --> F[Diretório de Arquivos Estáticos]
    subgraph VPS (jink.host)
        B
        C
        D
        E
        F
    end
```

**Fluxo de Requisições:**

1.  O cliente (navegador web) envia uma requisição HTTP/HTTPS para o endereço IP ou domínio da sua VPS.
2.  O Nginx, atuando como proxy reverso, recebe a requisição.
3.  Se a requisição for para um arquivo estático (CSS, JS, imagem), o Nginx serve diretamente do diretório de arquivos estáticos.
4.  Se a requisição for para uma URL da aplicação Django, o Nginx a encaminha para o Gunicorn.
5.  O Gunicorn executa a aplicação Django, que processa a requisição.
6.  A aplicação Django interage com o banco de dados PostgreSQL para ler ou gravar dados.
7.  A resposta da aplicação Django é enviada de volta ao Gunicorn, que a repassa ao Nginx.
8.  O Nginx envia a resposta final de volta ao cliente.

Este planejamento estabelece a base para a configuração detalhada da VPS, garantindo que todos os componentes necessários estejam presentes e configurados para trabalhar em conjunto de forma eficiente e segura.



---

## 💡 Parte 2: Configuração Inicial da VPS

Após adquirir sua VPS na jink.host, o primeiro passo é realizar a configuração inicial do servidor. Isso inclui acesso via SSH, atualização do sistema, criação de um novo usuário com privilégios sudo e configuração básica de segurança.

### 2.1 Acesso SSH à VPS

Você receberá as credenciais de acesso (IP do servidor, nome de usuário - geralmente `root` - e senha) da jink.host. Utilize um terminal para se conectar via SSH:

```bash
ssh root@SEU_IP_DA_VPS
```

Substitua `SEU_IP_DA_VPS` pelo endereço IP fornecido pela jink.host. Ao se conectar pela primeira vez, você pode ser solicitado a confirmar a chave SSH do servidor. Digite `yes` e pressione Enter.

### 2.2 Atualização do Sistema

É crucial garantir que o sistema operacional da sua VPS esteja atualizado para incluir as últimas correções de segurança e pacotes. Após o login, execute os seguintes comandos:

```bash
sudo apt update
sudo apt upgrade -y
```

*   `sudo apt update`: Atualiza a lista de pacotes disponíveis nos repositórios.
*   `sudo apt upgrade -y`: Atualiza todos os pacotes instalados para suas versões mais recentes. O `-y` confirma automaticamente todas as perguntas.

### 2.3 Criação de um Novo Usuário com Privilégios Sudo

É uma boa prática de segurança evitar usar o usuário `root` para tarefas diárias. Crie um novo usuário e conceda a ele privilégios sudo:

```bash
sudo adduser seu_usuario
```

Substitua `seu_usuario` pelo nome de usuário desejado. Você será solicitado a definir uma senha e algumas informações opcionais. Em seguida, adicione o novo usuário ao grupo `sudo`:

```bash
sudo usermod -aG sudo seu_usuario
```

Agora, saia da sessão `root` e faça login com o novo usuário:

```bash
exit
ssh seu_usuario@SEU_IP_DA_VPS
```

### 2.4 Configuração do Firewall (UFW)

O Uncomplicated Firewall (UFW) é uma interface mais simples para gerenciar regras de firewall no Linux. Configure-o para permitir apenas o tráfego essencial:

```bash
sudo ufw allow OpenSSH
sudo ufw enable
sudo ufw status
```

*   `sudo ufw allow OpenSSH`: Permite conexões SSH (porta 22 por padrão), garantindo que você não perca o acesso ao servidor.
*   `sudo ufw enable`: Ativa o firewall. Você será avisado de que isso pode interromper conexões SSH existentes; confirme com `y`.
*   `sudo ufw status`: Verifica o status do firewall e as regras ativas.

Posteriormente, adicionaremos regras para HTTP (porta 80) e HTTPS (porta 443) quando configurarmos o Nginx.

### 2.5 Configuração de Fuso Horário

Defina o fuso horário correto para o seu servidor. Isso é importante para logs e agendamento de tarefas:

```bash
sudo timedatectl set-timezone America/Sao_Paulo
```

Você pode listar os fusos horários disponíveis com `timedatectl list-timezones`.

Com a configuração inicial concluída, sua VPS está pronta para a instalação dos componentes da aplicação.



---

## 💡 Parte 3: Instalação e Configuração do PostgreSQL

O PostgreSQL será o sistema de gerenciamento de banco de dados para sua aplicação Django. Nesta seção, abordaremos a instalação, a criação de um novo usuário e banco de dados, e a configuração de acesso.

### 3.1 Instalação do PostgreSQL

Instale o servidor PostgreSQL e suas dependências na sua VPS:

```bash
sudo apt install postgresql postgresql-contrib -y
```

Após a instalação, o serviço PostgreSQL será iniciado automaticamente. Você pode verificar o status com:

```bash
sudo systemctl status postgresql
```

### 3.2 Criação de Usuário e Banco de Dados para o Django

Por padrão, o PostgreSQL cria um usuário `postgres` que tem acesso administrativo ao banco de dados. Precisaremos criar um novo usuário e um banco de dados para a sua aplicação Django. Isso é uma boa prática de segurança para isolar os privilégios da aplicação.

Primeiro, acesse o prompt do PostgreSQL como o usuário `postgres`:

```bash
sudo -i -u postgres psql
```

Dentro do prompt `psql`, crie um novo usuário para o seu banco de dados. Substitua `django_user` pelo nome de usuário desejado e `sua_senha_segura` por uma senha forte:

```sql
CREATE USER django_user WITH PASSWORD 'sua_senha_segura';
```

Em seguida, crie o banco de dados para a sua aplicação. Substitua `django_db` pelo nome do banco de dados desejado e `django_user` pelo usuário que você acabou de criar:

```sql
CREATE DATABASE django_db OWNER django_user;
```

Para garantir que o usuário `django_user` possa criar tabelas e gerenciar o banco de dados, conceda-lhe todos os privilégios no banco de dados `django_db`:

```sql
GRANT ALL PRIVILEGES ON DATABASE django_db TO django_user;
```

Agora, saia do prompt `psql`:

```sql
\q
```

### 3.3 Configuração de Acesso Remoto (Opcional e com Cautela)

Por padrão, o PostgreSQL só aceita conexões locais. Se você precisar acessar o banco de dados de uma máquina externa (por exemplo, para ferramentas de administração de banco de dados), você precisará configurar o acesso remoto. **No entanto, para a maioria das aplicações Django hospedadas na mesma VPS, isso não é necessário e pode introduzir riscos de segurança se não for configurado corretamente.**

Se for estritamente necessário, siga estes passos:

1.  **Edite `postgresql.conf`**: Abra o arquivo de configuração principal do PostgreSQL. O caminho pode variar ligeiramente dependendo da versão do Ubuntu, mas geralmente é algo como `/etc/postgresql/VERSAO/main/postgresql.conf` (substitua `VERSAO` pela versão do PostgreSQL instalada, por exemplo, `14` ou `16`).

    ```bash
sudo nano /etc/postgresql/VERSAO/main/postgresql.conf
    ```

    Procure pela linha `listen_addresses` e descomente-a (remova o `#` se houver) e altere seu valor para `'*'` para permitir conexões de qualquer endereço IP, ou para o IP específico da máquina que irá se conectar:

    ```
    listen_addresses = '*'
    ```

2.  **Edite `pg_hba.conf`**: Este arquivo controla a autenticação de clientes. Abra-o:

    ```bash
sudo nano /etc/postgresql/VERSAO/main/pg_hba.conf
    ```

    Adicione uma linha no final do arquivo para permitir conexões do seu IP externo. Substitua `SEU_IP_EXTERNO` pelo IP da máquina que você usará para conectar e `django_user` pelo nome do seu usuário do PostgreSQL:

    ```
    host    django_db       django_user       SEU_IP_EXTERNO/32         md5
    ```

    Se você quiser permitir conexões de qualquer IP (não recomendado para produção), use `0.0.0.0/0` em vez de `SEU_IP_EXTERNO/32`.

3.  **Reinicie o PostgreSQL**: Após as alterações, reinicie o serviço para que as novas configurações sejam aplicadas:

    ```bash
sudo systemctl restart postgresql
    ```

4.  **Configure o Firewall (UFW)**: Se você habilitou o acesso remoto, precisará abrir a porta padrão do PostgreSQL (5432) no seu firewall:

    ```bash
sudo ufw allow 5432/tcp
    ```

Com o PostgreSQL configurado, o próximo passo é preparar o ambiente Python e a aplicação Django na VPS.



---

## 💡 Parte 4: Configuração do Ambiente Python e Deploy do Django

Com o PostgreSQL instalado e configurado, o próximo passo é preparar o ambiente Python na VPS e realizar o deploy da sua aplicação Django.

### 4.1 Instalação do Python e Ferramentas Essenciais

Instale o Python 3, pip (gerenciador de pacotes) e `venv` (para ambientes virtuais):

```bash
sudo apt install python3 python3-pip python3-venv -y
```

### 4.2 Clonando o Repositório do Projeto Django

Navegue até o diretório onde você deseja armazenar seu projeto (por exemplo, `/var/www/`). É uma boa prática criar um diretório para seus projetos web:

```bash
sudo mkdir -p /var/www/seu_projeto_django
cd /var/www/seu_projeto_django
```

Agora, clone seu repositório Git. Certifique-se de que o usuário `seu_usuario` (criado na Parte 2) tenha permissões para escrever neste diretório. Se você clonar como `root`, precisará ajustar as permissões posteriormente.

```bash
sudo git clone SEU_URL_DO_REPOSITORIO .
```

Substitua `SEU_URL_DO_REPOSITORIO` pela URL do seu repositório GitHub/GitLab/Bitbucket. O `.` no final clona o conteúdo para o diretório atual.

### 4.3 Criação e Ativação do Ambiente Virtual

Crie um ambiente virtual Python dentro do diretório do seu projeto. Isso isolará as dependências do seu projeto do sistema:

```bash
python3 -m venv venv
source venv/bin/activate
```

Você verá `(venv)` no início do seu prompt, indicando que o ambiente virtual está ativo.

### 4.4 Instalação das Dependências do Projeto

Com o ambiente virtual ativo, instale as dependências do seu projeto Django listadas no `requirements.txt`:

```bash
pip install -r requirements.txt
```

Certifique-se de que `psycopg2-binary`, `dj-database-url`, `gunicorn` e `whitenoise` estejam incluídos no seu `requirements.txt`, conforme mencionado nos materiais base.

### 4.5 Configuração do `settings.py` para Produção

Edite o arquivo `settings.py` do seu projeto Django para se adaptar ao ambiente de produção na VPS. As alterações são semelhantes às feitas para o Vercel, mas com foco nas variáveis de ambiente do servidor e na conexão com o PostgreSQL local.

Abra `seu_projeto/settings.py` (substitua `seu_projeto` pelo nome real da sua pasta de projeto Django):

```bash
nano seu_projeto/settings.py
```

Certifique-se de que as seguintes configurações estejam presentes e corretas:

*   **`SECRET_KEY`**: Deve ser lida de uma variável de ambiente. Crie um arquivo `.env` na raiz do seu projeto na VPS ou defina-a diretamente no arquivo de serviço do Gunicorn (abordado na próxima seção).

    ```python
    from decouple import config
    SECRET_KEY = config("SECRET_KEY")
    ```

*   **`DEBUG`**: Defina como `False` em produção.

    ```python
    DEBUG = config("DEBUG", default=False, cast=bool)
    ```

*   **`ALLOWED_HOSTS`**: Inclua o endereço IP da sua VPS e o domínio (se você tiver um) que apontará para ela.

    ```python
    ALLOWED_HOSTS = ["SEU_IP_DA_VPS", "seu_dominio.com", "www.seu_dominio.com"]
    ```

*   **`DATABASES`**: Configure para usar o PostgreSQL que você instalou na VPS. Use `dj-database-url` para simplificar a configuração, lendo de uma `DATABASE_URL` que você definirá como variável de ambiente.

    ```python
    import dj_database_url

    DATABASES = {
        "default": dj_database_url.config(
            default=config("DATABASE_URL"),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
    ```

    A `DATABASE_URL` terá o formato:

    ```
    postgresql://django_user:sua_senha_segura@localhost:5432/django_db
    ```

    Substitua `django_user`, `sua_senha_segura` e `django_db` pelos valores que você definiu na Parte 3. `localhost` é usado porque o banco de dados está na mesma máquina.

*   **Arquivos Estáticos (`STATIC_ROOT`, `STATIC_URL`, `STATICFILES_STORAGE`)**: Configure o `whitenoise` para servir arquivos estáticos de forma eficiente. Certifique-se de que `whitenoise.middleware.WhiteNoiseMiddleware` esteja no seu `MIDDLEWARE`.

    ```python
    import os

    STATIC_URL = "/static/"
    STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
    ```

    E no `MIDDLEWARE`:

    ```python
    MIDDLEWARE = [
        # ...
        "whitenoise.middleware.WhiteNoiseMiddleware",
        # ...
    ]
    ```

Após as alterações, salve e feche o arquivo (`Ctrl+X`, `Y`, `Enter` no `nano`).

### 4.6 Coleta de Arquivos Estáticos e Migrações

Com o ambiente virtual ativo e o `settings.py` configurado, execute os comandos para coletar os arquivos estáticos e aplicar as migrações do banco de dados:

```bash
python manage.py collectstatic --noinput
python manage.py migrate
```

*   `collectstatic`: Reúne todos os arquivos estáticos de seus aplicativos Django e de terceiros em um único diretório (`STATIC_ROOT`).
*   `migrate`: Aplica as migrações pendentes ao seu banco de dados PostgreSQL, criando as tabelas necessárias.

### 4.7 Teste do Gunicorn

Antes de configurar o Nginx, teste se o Gunicorn consegue servir sua aplicação Django. Certifique-se de que o ambiente virtual esteja ativo:

```bash
gunicorn --bind 0.0.0.0:8000 seu_projeto.wsgi:application
```

Substitua `seu_projeto` pelo nome da sua pasta de projeto Django. Se tudo estiver correto, o Gunicorn iniciará e você verá mensagens indicando que ele está ouvindo na porta 8000. Você pode tentar acessar `http://SEU_IP_DA_VPS:8000` no seu navegador para verificar (lembre-se de abrir a porta 8000 no UFW se estiver testando de fora da VPS: `sudo ufw allow 8000/tcp`). Pressione `Ctrl+C` para parar o Gunicorn.

Com o Gunicorn funcionando, estamos prontos para configurar o Nginx como proxy reverso.



---

## 💡 Parte 5: Configuração do Nginx como Proxy Reverso

O Nginx atuará como o servidor web que receberá as requisições dos usuários e as encaminhará para o Gunicorn, além de servir os arquivos estáticos do seu projeto Django.

### 5.1 Instalação do Nginx

Instale o Nginx na sua VPS:

```bash
sudo apt install nginx -y
```

Após a instalação, o Nginx será iniciado automaticamente. Você pode verificar o status com:

```bash
sudo systemctl status nginx
```

### 5.2 Configuração do Firewall para Nginx

Permita o tráfego HTTP (porta 80) e HTTPS (porta 443) no UFW. Se você já permitiu SSH, pode desabilitar a regra de porta 8000 que usamos para teste do Gunicorn.

```bash
sudo ufw allow 'Nginx Full'
sudo ufw delete allow 8000/tcp # Se você adicionou essa regra para teste
sudo ufw status
```

`Nginx Full` é um perfil pré-definido do UFW que abre as portas 80 (HTTP) e 443 (HTTPS).

### 5.3 Criação do Arquivo de Configuração do Nginx para o Projeto Django

Crie um novo arquivo de configuração para o seu projeto Django no diretório `sites-available` do Nginx:

```bash
sudo nano /etc/nginx/sites-available/seu_projeto_django
```

Adicione o seguinte conteúdo ao arquivo, substituindo `seu_projeto_django` pelo nome do seu projeto, `SEU_IP_DA_VPS` pelo IP do seu servidor e `seu_dominio.com` pelo seu domínio (se aplicável):

```nginx
server {
    listen 80;
    server_name SEU_IP_DA_VPS seu_dominio.com www.seu_dominio.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /var/www/seu_projeto_django;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
}
```

**Explicação da Configuração:**

*   `listen 80;`: O Nginx escutará na porta 80 para requisições HTTP.
*   `server_name SEU_IP_DA_VPS seu_dominio.com www.seu_dominio.com;`: Define os nomes de host que este bloco de servidor responderá. Inclua o IP da sua VPS e seus domínios.
*   `location /static/`: Esta diretiva informa ao Nginx para servir os arquivos estáticos localizados em `/var/www/seu_projeto_django/staticfiles` diretamente. Isso é mais eficiente do que deixar o Django servir esses arquivos.
*   `location /`: Esta diretiva captura todas as outras requisições e as encaminha para o Gunicorn através de um socket Unix (`http://unix:/run/gunicorn.sock`).
*   `include proxy_params;`: Inclui um conjunto de parâmetros de proxy padrão do Nginx, que são úteis para passar informações da requisição para o Gunicorn.

Salve e feche o arquivo.

### 5.4 Ativação do Arquivo de Configuração

Crie um link simbólico do seu arquivo de configuração em `sites-available` para o diretório `sites-enabled` para ativá-lo:

```bash
sudo ln -s /etc/nginx/sites-available/seu_projeto_django /etc/nginx/sites-enabled/
```

Remova o arquivo de configuração padrão do Nginx para evitar conflitos:

```bash
sudo rm /etc/nginx/sites-enabled/default
```

### 5.5 Teste e Reinício do Nginx

Teste a sintaxe da configuração do Nginx para garantir que não há erros:

```bash
sudo nginx -t
```

Se a sintaxe estiver OK, reinicie o Nginx para aplicar as novas configurações:

```bash
sudo systemctl restart nginx
```

Com o Nginx configurado, o próximo passo é configurar o Gunicorn para ser executado como um serviço do `systemd`.



---

## 💡 Parte 6: Configuração do Gunicorn como Serviço systemd

Para garantir que o Gunicorn inicie automaticamente com o servidor e seja gerenciado de forma robusta, configuraremos ele como um serviço `systemd`.

### 6.1 Criação do Arquivo de Serviço do Gunicorn

Crie um novo arquivo de serviço para o Gunicorn:

```bash
sudo nano /etc/systemd/system/gunicorn.service
```

Adicione o seguinte conteúdo, substituindo `seu_usuario` pelo nome do usuário que você criou na Parte 2, `seu_projeto_django` pelo nome do diretório do seu projeto e `seu_projeto` pelo nome da sua pasta de projeto Django (onde o `wsgi.py` está localizado):

```ini
[Unit]
Description=Gunicorn instance to serve seu_projeto_django
After=network.target

[Service]
User=seu_usuario
Group=www-data
WorkingDirectory=/var/www/seu_projeto_django
ExecStart=/var/www/seu_projeto_django/venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/run/gunicorn.sock seu_projeto.wsgi:application

[Install]
WantedBy=multi-user.target
```

**Explicação da Configuração:**

*   `Description`: Uma descrição para o serviço.
*   `After=network.target`: Garante que o serviço Gunicorn só inicie após a rede estar disponível.
*   `User` e `Group`: Define o usuário e grupo sob os quais o Gunicorn será executado. `www-data` é um grupo comum para processos de servidor web.
*   `WorkingDirectory`: O diretório raiz do seu projeto Django.
*   `ExecStart`: O comando para iniciar o Gunicorn. Ele usa o executável `gunicorn` do seu ambiente virtual, define o log de acesso para a saída padrão, especifica 3 workers (ajuste conforme a necessidade do seu servidor e carga), e vincula o Gunicorn a um socket Unix (`/run/gunicorn.sock`), que é o mesmo socket que o Nginx está configurado para usar.
*   `[Install]`: Define quando o serviço deve ser iniciado automaticamente (neste caso, no nível de execução multi-usuário).

Salve e feche o arquivo.

### 6.2 Criação do Arquivo de Socket do Gunicorn (Opcional, mas recomendado)

Embora o Gunicorn possa criar o socket, é uma boa prática ter um arquivo de socket `systemd` separado para maior controle e para garantir que o socket seja criado com as permissões corretas. Crie o arquivo:

```bash
sudo nano /etc/systemd/system/gunicorn.socket
```

Adicione o seguinte conteúdo:

```ini
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
```

Salve e feche o arquivo.

### 6.3 Habilitar e Iniciar os Serviços Gunicorn

Recarregue o `systemd` para reconhecer os novos arquivos de serviço e socket:

```bash
sudo systemctl daemon-reload
```

Habilite e inicie o socket do Gunicorn (o serviço será iniciado automaticamente quando uma conexão for feita ao socket):

```bash
sudo systemctl enable gunicorn.socket
sudo systemctl start gunicorn.socket
```

Verifique o status do socket e do serviço:

```bash
sudo systemctl status gunicorn.socket
sudo systemctl status gunicorn.service
```

Você deve ver que ambos estão `active (running)`. Se o serviço Gunicorn não estiver ativo, tente iniciá-lo manualmente:

```bash
sudo systemctl start gunicorn.service
```

Se houver erros, verifique os logs do Gunicorn para depuração:

```bash
sudo journalctl -u gunicorn.service -f
```

### 6.4 Teste Final da Aplicação

Com o Nginx e o Gunicorn configurados, sua aplicação Django deve estar acessível via HTTP. Abra seu navegador e navegue para o endereço IP da sua VPS ou para o domínio que você configurou. Você deve ver sua aplicação Django funcionando.

Se você encontrar problemas, verifique os logs do Nginx (`sudo tail -f /var/log/nginx/error.log`) e do Gunicorn (`sudo journalctl -u gunicorn.service -f`).

---

## 💡 Parte 7: Configuração de HTTPS com Certbot (Let's Encrypt)

É fundamental proteger sua aplicação com HTTPS para garantir a segurança dos dados e a confiança dos usuários. Usaremos o Certbot para obter e configurar certificados SSL/TLS gratuitos do Let's Encrypt.

### 7.1 Instalação do Certbot

Instale o Certbot e o plugin Nginx para ele:

```bash
sudo snap install core
sudo snap refresh core
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot
sudo apt install python3-certbot-nginx -y
```

### 7.2 Obtenção do Certificado SSL

Execute o Certbot para obter e instalar o certificado. Certifique-se de que seu domínio esteja apontando para o IP da sua VPS antes de executar este comando.

```bash
sudo certbot --nginx -d seu_dominio.com -d www.seu_dominio.com
```

*   Substitua `seu_dominio.com` e `www.seu_dominio.com` pelos seus domínios reais.
*   O Certbot fará algumas perguntas, como seu endereço de e-mail para avisos de expiração e se você concorda com os termos de serviço. Ele também perguntará se você deseja redirecionar todo o tráfego HTTP para HTTPS (recomendado).

Após a conclusão bem-sucedida, o Certbot modificará automaticamente a configuração do Nginx para incluir o certificado SSL e configurar o redirecionamento HTTP para HTTPS.

### 7.3 Verificação da Renovação Automática

O Certbot configura automaticamente um cron job ou um timer do `systemd` para renovar seus certificados antes que expirem. Você pode testar o processo de renovação com um "dry run":

```bash
sudo certbot renew --dry-run
```

Se este comando for executado sem erros, suas renovações automáticas estão configuradas corretamente.

---

## 💡 Parte 8: Gerenciamento e Manutenção

Esta seção aborda práticas essenciais para o gerenciamento contínuo da sua aplicação Django e VPS.

### 8.1 Atualizações do Projeto Django

Para atualizar seu projeto Django na VPS (após fazer push de novas alterações para o seu repositório Git):

1.  **Acesse a VPS via SSH** com seu usuário.
2.  **Navegue até o diretório do projeto**:
    ```bash
    cd /var/www/seu_projeto_django
    ```
3.  **Ative o ambiente virtual**:
    ```bash
    source venv/bin/activate
    ```
4.  **Puxe as últimas alterações do Git**:
    ```bash
    git pull origin main # ou o nome da sua branch principal
    ```
5.  **Instale novas dependências (se houver)**:
    ```bash
    pip install -r requirements.txt
    ```
6.  **Execute as migrações do banco de dados (se houver)**:
    ```bash
    python manage.py migrate
    ```
7.  **Colete arquivos estáticos (se houver alterações nos estáticos)**:
    ```bash
    python manage.py collectstatic --noinput
    ```
8.  **Reinicie o Gunicorn para aplicar as alterações**:
    ```bash
    sudo systemctl restart gunicorn.service
    ```

### 8.2 Backup do Banco de Dados PostgreSQL

É crucial fazer backups regulares do seu banco de dados. Para criar um backup do `django_db`:

```bash
sudo -u postgres pg_dump django_db > /caminho/para/seu/backup/django_db_backup_$(date +%Y%m%d%H%M%S).sql
```

Substitua `/caminho/para/seu/backup/` por um diretório seguro onde você deseja armazenar os backups. Considere automatizar este processo com um cron job.

Para restaurar um backup:

```bash
sudo -u postgres psql -d django_db -f /caminho/para/seu/backup/nome_do_backup.sql
```

### 8.3 Monitoramento de Logs

Monitore os logs para identificar problemas:

*   **Nginx**: `sudo tail -f /var/log/nginx/access.log` e `sudo tail -f /var/log/nginx/error.log`
*   **Gunicorn**: `sudo journalctl -u gunicorn.service -f`
*   **PostgreSQL**: Os logs do PostgreSQL geralmente estão em `/var/log/postgresql/`.

### 8.4 Atualizações do Sistema Operacional

Periodicamente, execute as atualizações do sistema para manter a segurança e estabilidade:

```bash
sudo apt update
sudo apt upgrade -y
```

---

## 💡 Parte 9: Troubleshooting (Resolução de Problemas Comuns)

### Problema: Aplicação não acessível ou "502 Bad Gateway"

*   **Verifique o Gunicorn**: O Gunicorn está rodando? `sudo systemctl status gunicorn.service`. Se não, verifique os logs: `sudo journalctl -u gunicorn.service -f`.
*   **Verifique o Nginx**: O Nginx está rodando? `sudo systemctl status nginx`. Verifique a configuração: `sudo nginx -t`. Verifique os logs: `sudo tail -f /var/log/nginx/error.log`.
*   **Permissões**: Certifique-se de que o usuário `seu_usuario` e o grupo `www-data` têm permissões de leitura e execução nos arquivos do projeto Django e no socket do Gunicorn.

### Problema: Erros de Conexão com o Banco de Dados

*   **Verifique o PostgreSQL**: O PostgreSQL está rodando? `sudo systemctl status postgresql`. Verifique os logs do PostgreSQL.
*   **Credenciais**: As credenciais (`django_user`, `sua_senha_segura`, `django_db`) no `settings.py` estão corretas e correspondem às do PostgreSQL?
*   **Firewall**: A porta 5432 está aberta no UFW se você estiver tentando conectar remotamente? (Não necessário se o Django e o PostgreSQL estão na mesma VPS).

### Problema: Arquivos Estáticos não Carregam

*   **`collectstatic`**: Você executou `python manage.py collectstatic` após as últimas alterações?
*   **Caminho `STATIC_ROOT`**: O `STATIC_ROOT` no `settings.py` está correto e o Nginx está apontando para o diretório certo (`/var/www/seu_projeto_django/staticfiles`)?
*   **Permissões**: O Nginx tem permissão para ler os arquivos no diretório `STATIC_ROOT`?

### Problema: Erros de Permissão

*   Use `ls -l` para verificar as permissões de arquivos e diretórios. Use `sudo chown -R seu_usuario:www-data /var/www/seu_projeto_django` para definir o proprietário e o grupo corretos, e `sudo chmod -R 755 /var/www/seu_projeto_django` para definir permissões de leitura/execução para o grupo e outros.

---

## ✅ Checklist Final para Migração para VPS

Antes de considerar a migração completa, revise este checklist:

- [ ] VPS provisionada na jink.host e acessível via SSH.
- [ ] Sistema operacional atualizado.
- [ ] Novo usuário com privilégios sudo criado e configurado.
- [ ] Firewall (UFW) configurado para permitir SSH, HTTP e HTTPS.
- [ ] Fuso horário do servidor configurado.
- [ ] PostgreSQL instalado e configurado com usuário e banco de dados dedicados para o Django.
- [ ] Python, pip e `venv` instalados.
- [ ] Repositório Django clonado para a VPS.
- [ ] Ambiente virtual criado e ativado.
- [ ] Dependências do projeto instaladas (`requirements.txt`).
- [ ] `settings.py` do Django configurado para produção (DEBUG=False, ALLOWED_HOSTS, DATABASE_URL, STATIC_ROOT, etc.).
- [ ] `python manage.py collectstatic` executado.
- [ ] `python manage.py migrate` executado.
- [ ] Gunicorn instalado e configurado como serviço `systemd`.
- [ ] Nginx instalado e configurado como proxy reverso para o Gunicorn e para servir arquivos estáticos.
- [ ] Certificado SSL/TLS (HTTPS) configurado com Certbot (Let's Encrypt).
- [ ] Aplicação Django acessível via domínio/IP e HTTPS.
- [ ] Admin Django funcionando e acessível.
- [ ] Arquivos estáticos carregando corretamente.
- [ ] Estratégia de backup do banco de dados definida.
- [ ] Processo de atualização do projeto na VPS compreendido.

---

🎉 **Parabéns!** Você migrou com sucesso seu backend Django com PostgreSQL do Vercel para uma VPS da jink.host!

> **Dica Pro**: Considere usar ferramentas de automação de provisionamento como Ansible ou Docker para gerenciar seu ambiente de produção de forma mais eficiente e replicável no futuro.

## Referências

[1] PostgreSQL. *The world's most advanced open source relational database.* Disponível em: [https://www.postgresql.org/](https://www.postgresql.org/)

[2] Nginx. *High-performance HTTP server, reverse proxy, and load balancer.* Disponível em: [https://nginx.org/](https://nginx.org/)

[3] Gunicorn. *A Python WSGI HTTP Server for Unix.* Disponível em: [https://gunicorn.org/](https://gunicorn.org/)

[4] Django. *The Web framework for perfectionists with deadlines.* Disponível em: [https://www.djangoproject.com/](https://www.djangoproject.com/)

[5] Let's Encrypt. *A free, automated, and open Certificate Authority.* Disponível em: [https://letsencrypt.org/](https://letsencrypt.org/)

[6] Certbot. *Automatically enable HTTPS on your website with EFF's Certbot, a free and open source tool.* Disponível em: [https://certbot.eff.org/](https://certbot.eff.org/)

[7] jink.host. *Affordable Gaming & Cloud Hosting.* Disponível em: [https://jink.host/](https://jink.host/)


