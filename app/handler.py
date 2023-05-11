import boto3
import json
import pymysql
import os

def lambda_handler(event, context):
    
    # Leitura dos dados da requisição
    token = event['token']
    
    # Conexão com o banco de dados
    secretsmanager = boto3.client('secretsmanager')
    response = secretsmanager.get_secret_value(SecretId=f'replenish4me-db-password-{os.environ.get("env", "dev")}')
    db_password = response['SecretString']
    rds = boto3.client('rds')
    response = rds.describe_db_instances(DBInstanceIdentifier=f'replenish4medatabase{os.environ.get("env", "dev")}')
    endpoint = response['DBInstances'][0]['Endpoint']['Address']
    # Conexão com o banco de dados
    with pymysql.connect(
        host=endpoint,
        user='admin',
        password=db_password,
        database='replenish4me'
    ) as conn:
    
        # Verificação da sessão ativa no banco de dados
        with conn.cursor() as cursor:
            sql = "SELECT usuario_id FROM SessoesAtivas WHERE id = %s"
            cursor.execute(sql, (token,))
            result = cursor.fetchone()
            
            if result is None:
                response = {
                    "statusCode": 401,
                    "body": json.dumps({"message": "Sessão inválida"})
                }
                return response
            
            usuario_id = result[0]
            
            # Busca dos leitores relacionados ao usuário
            sql = "SELECT id FROM Leitores WHERE usuario_id = %s"
            cursor.execute(sql, (usuario_id,))
            result = cursor.fetchall()
            
            leitores = [row[0] for row in result]
            
            conn.commit()

    # Retorno da resposta da função
    response = {
        "statusCode": 200,
        "body": json.dumps({"leitores": leitores})
    }
    return response
