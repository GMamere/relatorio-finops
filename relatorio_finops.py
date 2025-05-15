import os
import requests
from jinja2 import Environment, FileSystemLoader
import pdfkit
from dotenv import load_dotenv
from datetime import datetime

# Carrega variáveis do .env
load_dotenv()
API_KEY = os.getenv("CLOUDCHECKR_API_KEY")
ACCOUNT_NAME = os.getenv("CLOUDCHECKR_ACCOUNT_NAME")

# Caminho do wkhtmltopdf no Windows (ajuste se necessário)
WKHTMLTOPDF_PATH = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)


def obter_dados_cloudcheckr():
    url = "https://app.cloudcheckr.com/api/billing.json/get_billing_summary_v4"
    params = {
        "access_key": API_KEY,
        "account_name": ACCOUNT_NAME,
        "month": datetime.now().month,
        "year": datetime.now().year
    }

    try:
        print("🔄 Consultando CloudCheckr...")
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        print("✅ Dados obtidos da API.")
        return response.json()

    except Exception as e:
        print(f"⚠️ Erro ao consultar CloudCheckr: {e}")
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
