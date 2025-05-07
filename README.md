# Projeto Final ASA

Este projeto implementa um protótipo de microserviços para uma companhia aérea de venda de passagens, conforme requisitos:

- Ambiente linux através de wsl
- Linguagem: Python (Flask)
- Banco de dados: PostgreSQL (externo/not containerized)
- Containerização: Docker (Ubuntu 20.04) para cada serviço

## Estrutura do Projeto

- `db/schema.sql`: script de criação do banco de dados PostgreSQL
- `auth_service`: serviço de autenticação (login, logout, validação de sessão)
- `airports_service`: serviço de aeroportos (listagem e destinos)
- `flights_service`: serviço de voos (listagem por data e pesquisa)
- `purchase_service`: serviço de compras (reserva e emissão de tickets)

## Banco de Dados

- Instale o PostgreSQL localmente ou em servidor externo.
```bash
sudo apt update

sudo apt install postgresql postgresql-contrib
```
    
- Entre no postgres e crie a database
```bash
sudo -i -u postgres

createdb airlines
```

- Entre no database e execute `db/schema.sql` para criar as tabelas e ativar a extensão.
    - psql -h <host> -U <user> -d airlines -f db/schema.sql
    - exemplo: user postgres e password 1234
```bash
psql -h localhost -U postgres -d airlines -f db/schema.sql
```

- Em airlines, testar usando "\dt" para garantir que as tabelas foram criadas

- Entre no database para checar tabelas com os selects
    - psql -h localhost -U postgres -d airlines

- Selects
```bash
SELECT * FROM users WHERE email='teste@ex.com';

SELECT id, code, city FROM airports;

SELECT id, flight_number, origin_id, destination_id, price FROM flights;
```

## Como executar com Docker

- Através do docker-compose.yml, é possível build e run a imagem:
```bash
docker-compose up --build -d
```

## Explicação

Cada microserviço expõe endpoints JSON na porta 5000.

## Confirmando os containers (opcional)

- Confirme
```bash
docker ps --filter "name=auth" --filter "name=airports" --filter "name=flights" --filter "name=purchase"
```

- Teste a conexão dentro do container
```bash
docker exec -it auth bash -c "apt-get update && apt-get install -y postgresql-client && psql -h host.docker.internal -U codey -d airlines -c '\dt'"
```

## Testes com curl:

- Login (supondo usuário criado no DB)
```bash
curl -X POST http://localhost:5001/login \
-H 'Content-Type: application/json' \
-d '{"email":"teste@ex.com","password":"123456"}'
```
- Resposta esperada:
{"expires_at":"2025-05-05T21:54:11.504746","session_key":"2601e29f-02de-48e1-b4b9-401fc5e11fde"}

--------------------------------------------------------------------------------------------------------------------------------------------

- Validar a sessão (usando a session key)
```bash
curl -G http://localhost:5001/validate_session \
--data-urlencode "session_key=97dcf78f-8ff8-44a3-a90e-6e6300e48968"
```
- Resposta esperada:
{"valid":true}

--------------------------------------------------------------------------------------------------------------------------------------------

- Listar todos os aeroportos
```bash
curl http://localhost:5002/airports
```
- Resposta esperada:
[{"city":"S\u00e3o Paulo","code":"GRU","id":1,"name":"Aeroporto de Guarulhos"},
{"city":"Rio de Janeiro","code":"GIG","id":2,"name":"Aeroporto do Gale\u00e3o"},
{"city":"Bras\u00edlia","code":"BSB","id":3,"name":"Aeroporto Internacional de Bras\u00edlia"}]

--------------------------------------------------------------------------------------------------------------------------------------------

- Listar aeroportos destino de acordo com o id do aeroporto origem
```bash
curl http://localhost:5002/airports/1/destinations
```
- Resposta esperada:
[{"city":"Rio de Janeiro","code":"GIG","id":2,"name":"Aeroporto do Gale\u00e3o"}]

--------------------------------------------------------------------------------------------------------------------------------------------

- Listar voos por data (exemplo usado: 2025-05-10)
```bash
curl "http://localhost:5003/flights?date=2025-05-10"
```
- Resposta esperada:
[{"arrival_time":"2025-05-10T10:00:00","departure_time":"2025-05-10T08:00:00","destination_id":2,"flight_number":"AZ123","id":1,"origin_id":1,"price":350.5},
{"arrival_time":"2025-05-10T14:30:00","departure_time":"2025-05-10T12:30:00","destination_id":1,"flight_number":"AZ456","id":2,"origin_id":2,"price":330.0}]

--------------------------------------------------------------------------------------------------------------------------------------------

- Buscar o voo mais barato entre dois aeroportos (usando origem, destino, data)
```bash
curl -X POST http://localhost:5003/search \
  -H 'Content-Type: application/json' \
  -d '{"origin_id":1,"destination_id":2,"date":"2025-05-10"}'
```
- Resposta esperada:
{"flight_id":1,"flight_number":"AZ123","passengers":1,"price":350.5}

--------------------------------------------------------------------------------------------------------------------------------------------

- Efetuar a compra (usando session key, id de vôo, número de passsageiros)
```bash
curl -X POST http://localhost:5004/purchase \
  -H 'Content-Type: application/json' \
  -d '{
    "session_key":"97dcf78f-8ff8-44a3-a90e-6e6300e48968",
    "flight_id":1,
    "passengers":1
  }'
```
- Resposta esperada
{"locator":"00f72d60","tickets":["30c9c490"]}

--------------------------------------------------------------------------------------------------------------------------------------------

- Logout
```bash
curl -X POST http://localhost:5001/logout \
-H 'Content-Type: application/json' \
-d '{"email":"teste@ex.com","password":"123456"}'
```
- Reposta esperada
{"message":"Logout realizado com sucesso"}

## Desligando os containeres
```bash
docker-compose down
```
