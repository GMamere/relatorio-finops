import os
import requests
from jinja2 import Environment, FileSystemLoader
import pdfkit
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
API_KEY = os.getenv("CLOUDCHECKR_API_KEY")
ACCOUNT_NAME = os.getenv("CLOUDCHECKR_ACCOUNT_NAME")

WKHTMLTOPDF_PATH = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)


def obter_dados_cloudcheckr():
    url = "https://api-us.cloudcheckr.com/graphql"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    month = datetime.now().month
    year = datetime.now().year

    query = f"""
    query {{
        spendOverview(
            filter: {{
                accountIds: ["{ACCOUNT_NAME}"],
                timeRange: {{ type: MONTH_TO_DATE }}
            }}
        ) {{
            totalCost
            unblendedCost
            amortizedCost
            forecastedCost
            currency
        }}
    }}
    """


    try:
        print("🔄 Enviando requisição para o CloudCheckr CMx GraphQL...")
        print("🔍 Payload da requisição:")
        print(query)

        response = requests.post(url, json={"query": query}, headers=headers, timeout=15)
        response.raise_for_status()

        print("✅ Resposta recebida:")
        print(response.json())

        data = response.json()['data']['billingSummary']
        return {
            "TotalCost": data['totalCost'],
            "ServiceBreakdown": [
                {"ServiceName": item['service'], "Cost": item['cost']}
                for item in data['serviceBreakdown']
            ],
            "CostByTag": [
                {"TagValue": item['tagValue'], "Cost": item['cost']}
                for item in data['costByTag']
            ]
        }

    except Exception as e:
        print(f"⚠️ Erro ao consultar CloudCheckr CMx: {e}")
        print("🔁 Usando dados simulados para testes.")
        return obter_dados_falsos_para_teste()
        
def obter_dados_falsos_para_teste():
    return {
        "TotalCost": 34500.00,
        "ServiceBreakdown": [
            {"ServiceName": "EC2", "Cost": 15000},
            {"ServiceName": "S3", "Cost": 5000},
            {"ServiceName": "RDS", "Cost": 4000},
            {"ServiceName": "Lambda", "Cost": 3000},
            {"ServiceName": "CloudWatch", "Cost": 2000}
        ],
        "CostByTag": [
            {"TagValue": "TI", "Cost": 18000},
            {"TagValue": "Financeiro", "Cost": 9000},
            {"TagValue": "Marketing", "Cost": 7500}
        ]
    }


def gerar_pdf(dados):
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('template_relatorio.html')

    html_out = template.render(
        mes=datetime.now().strftime("%B/%Y"),
        custo_total=dados['TotalCost'],
        top_servicos=dados['ServiceBreakdown'][:5],
        centros_custo=dados.get('CostByTag', []),
        oportunidades=[
            "Instâncias subutilizadas",
            "Volumes EBS não utilizados",
            "Reservas não aproveitadas",
            "S3 sem política de lifecycle"
        ],
        acoes_realizadas=["Desligamento de instâncias fora do horário comercial"],
        plano_proximo=["Ativar lifecycle no S3", "Revisar tags em contas"]
    )

    pdfkit.from_string(html_out, 'Relatorio_FinOps.pdf', configuration=config)
    print("📄 PDF gerado com sucesso: Relatorio_FinOps.pdf")


if __name__ == '__main__':
    dados = obter_dados_cloudcheckr()
    gerar_pdf(dados)
