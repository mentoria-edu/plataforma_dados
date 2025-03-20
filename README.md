# Mentoria-edu - Plataforma de dados

## Componentes Principais 

- **Apache Spark**: Framework de processamento distribuído para grandes volumes de dados.
- **HDFS (Hadoop Distributed File System)**: Sistema de armazenamento distribuído escalável e tolerante a falhas (base do ecossistema Hadoop).
- **Apache Hive**: Camada SQL sobre o HDFS para consultas estruturadas e gerenciamento de metadados do spark utilizando Derby.

## Estrutura

```
plataforma_dados/
├── hdfs/              
├── hive/
├── spark_standalone/
├── README.md

```

## Guia Commit - Git flow

### Estrutura de Branches do Git Flow

- `main`/`master`: Branch de produção (versões estáveis).
- `develop`: Branch de desenvolvimento integrado.
- `feat/*`: Branches para novas funcionalidades.
- `release/*`: Branches para preparação de versões.
- `hotfix/*`: Branches para correções críticas em produção.

#### Feature Branch:

```bash
git checkout develop
git pull origin develop
git checkout -b feature/nome-da-feature
```

#### Commits na Feature:
- Faça commits pequenos e focados.
- Use mensagens claras no padrão (ex: `feat: add user login button`).

```bash
git add .
git commit -m "feat: add user login button"
git push origin feature/nome-da-feature
```

#### Finalizar uma Feature:

**Pull Request (PR)**:

1. Acesse o repositório no GitHub.
2. Vá até a aba **Pull Requests**.
3. Clique em **New Pull Request**.
4. Selecione `feature/nome-da-feature` como origem e `develop` como destino.
5. Adicione a descrição com o mesmo nome da branch e envie para revisão.
---

### Release Branch: 

```bash
git checkout develop
git pull origin develop
git checkout -b release/v1.0.0  
```
#### Commits na Release:
- Commits devem seguir o padrão (ex: chore: update version to 1.0.0 ou fix: resolve login timeout).

```bash
git add .
git commit -m "chore: update version to 1.0.0"
git push origin release/v1.0.0
```

#### Finalizar a Release:

1. Acesse o repositório no GitHub.
2. Vá até a aba **Pull Requests**.
3. Clique em **New Pull Request**.
4. Selecione `release/v1.0.0` como origem e `main` como destino.
5. Adicione a descrição com o mesmo nome da branch e envie para revisão.
6. Crie uma tag com a versão no main:

```bash
git checkout main
git tag v1.0.0
git push origin v1.0.0
```
7. Faça um PR para atualizar a develop

### Hotfix Branch

```bash
git checkout main
git pull origin main
git checkout -b hotfix/nome-do-hotfix 
```
#### Commits Hotfix :

- Faça commits focados apenas na correção crítica (ex: fix: prevent null user data crash).

```bash
git add .
git commit -m "fix: prevent null user data crash"
git push origin hotfix/nome-do-hotfix
```

#### Finalizar Hotfix:

1. Acesse o repositório no GitHub.
2. Vá até a aba **Pull Requests**.
3. Clique em **New Pull Request**.
4. Crie um PR de `hotfix/nome-do-hotfix` para `main`
5. Adicione a descrição com o mesmo nome da branch e envie para revisão.
6. Crie uma tag com a nova versão no main (ex: v1.0.1):

```bash
git checkout main
git tag v1.0.1
git push origin v1.0.1
```
7. Faça um PR para atualizar a develop

### ❓ Dúvidas ou Ajuda?

[Documentação gitflow Atlassiam](https://www.atlassian.com/br/git/tutorials/comparing-workflows/gitflow-workflow)

