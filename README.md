# Ultra-Fast Discord Ticket Bot 🚀

Bot de resposta automática ultra-rápido para tickets do Discord, otimizado para latência mínima.

## Características

- ⚡ **Velocidade Extrema**: Resposta em <100ms
- 🎯 **Zero Duplicatas**: Proteção absoluta contra mensagens duplicadas
- 🔥 **Multi-Session**: Arquitetura otimizada para consistência
- 🌐 **Cloud Ready**: Configurado para ShardCloud

## Configuração

1. Edite o arquivo `.env` com suas credenciais:
```env
DISCORD_TOKEN=seu_token_aqui
CATEGORY_ID=id_da_categoria
RESPONSE_MSG=Sua mensagem de resposta
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute:
```bash
python main.py
```

## Hosting (ShardCloud)

1. Configure as variáveis de ambiente no painel da ShardCloud
2. Faça upload dos arquivos: `main.py`, `requirements.txt`, `.shardcloud`
3. O bot iniciará automaticamente

## Performance

- Latência típica: 10-50ms (hospedado nos EUA)
- Arquitetura single-shot para máxima velocidade
- DNS prefetching e connection pooling

## Aviso

⚠️ Self-bots violam os Termos de Serviço do Discord. Use por sua conta e risco.
