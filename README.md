# Mentoria-edu - Plataforma de dados

## Estrutura

```
plataforma_dados/
├── README.md

```

## Guia Commit - Git flow

### Estrutura de Branches do Git Flow

- `main`: Branch de produção.
- `dev`: Branch de desenvolvimento integrado.
- `feat/*`: Branches para novas funcionalidades.
- `hotfeat/*`: Branches para aplicar features críticas.
- `hotfix/*`: Branches para correções críticas em produção.

#### Feature Branch:

```bash
git checkout dev
git pull origin dev
git checkout -b feat/nome-da-feature
```

#### Commits na Feature:

```bash
git add "seu_arquivo_atualizado.ext"
git commit -m "feat: add user login button"
git push origin feat/nome-da-feature
```

#### Finalizar uma Feature:

**Pull Request (PR)**:

1. Acesse o repositório no GitHub.
2. Vá até a aba **Pull Requests**.
3. Clique em **New Pull Request**.
4. Selecione `feat/nome-da-feature` como origem e `dev` como destino.
5. Adicione a descrição com o mesmo nome da branch e envie para revisão.
---

### Hotfix/Hotfeat Branch

```bash
git checkout main
git pull origin main
git checkout -b hotfix/nome-do-hotfix 
```
#### Commits Hotfix/Hotfeat:

```bash
git add "seu_arquivo_atualizado.ext"
git commit -m "hotfix: prevent null user data crash"
git push origin hotfix/nome-do-hotfix
```

#### Finalizar Hotfix/Hotfeat:

1. Acesse o repositório no GitHub.
2. Vá até a aba **Pull Requests**.
3. Clique em **New Pull Request**.
4. Crie um PR de `hotfix/nome-do-hotfix` para `main`
5. Adicione a descrição com o mesmo nome da branch e envie para revisão.
6. Faça um PR para atualizar a branch dev

---

### Merge dev->main:

As features ficarão na branch dev para avaliação por uma semana, serão mescladas nos dias de review (segunda e quinta-feira), caso sejam aprovadas. ❗❗❗

---
### ❓ Dúvidas ou Ajuda?

[Documentação gitflow Atlassiam](https://www.atlassian.com/br/git/tutorials/comparing-workflows/gitflow-workflow)

