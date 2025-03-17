# Mentoria-edu - Plataforma de dados

## Descrição

Este repositório contém o código e os recursos necessários para desenvolvimento e aprimoramento de uma plataforma de dados. 

## Como realizar um Push para o repósitorio

###  1. Criando uma Nova Branch

```bash
# Crie uma nova branch para sua funcionalidade
git checkout -b feature/nova-funcionalidade
```

---

###  2. Fazendo Alterações e Commitando

Após modificar os arquivos, siga estes passos:

```bash
# Adicionar os arquivos modificados
git add .

# Criar um commit descritivo
git commit -m "feat: adiciona nova funcionalidade X"
```

---

###  3. Enviando a Branch para o Repositório

Agora, faça o **push** da branch remota:

```bash
# Enviar a branch para o repositório
git push origin feature/nova-funcionalidade
```

Se for a **primeira vez** enviando essa branch, use:

```bash
git push --set-upstream origin feature/nova-funcionalidade
```

---

### 4. Criando um Pull Request

1. Acesse o repositório no GitHub/GitLab.
2. Vá até a aba **Pull Requests**.
3. Clique em **New Pull Request**.
4. Selecione `feature/nova-funcionalidade` como origem e `main` como destino.
5. Adicione uma descrição e envie para revisão.

---


