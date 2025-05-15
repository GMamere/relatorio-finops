import requests
import pandas as pd
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from datetime import datetime

API_KEY = 'SUA_CLOUDCHECKR_API_KEY'
ACCOUNT_NAME = 'NOME_DA_CONTA'
BASE_URL = 'https://app.cloudcheckr.com/api/billing.json/get_billing_summary'

def obter_dados_cloudcheckr():
    params = {
        'access_key': API_KEY,
        'account_name': ACCOUNT_NAME,
        'month': datetime.now().month,
        'year': datetime.now().year
    }
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    return response.json()

def gerar_pdf(dados):
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('template_relatorio.html')
    
    html_out = template.render(
        mes=datetime.now().strftime("%B/%Y"),
        custo_total=dados['TotalCost'],
        top_servicos=dados['ServiceBreakdown'][:5],
        centros_custo=dados.get('CostByTag', []),
        variacoes=[],  # você pode comparar com cache anterior
        oportunidades=[
            "Instâncias subutilizadas",
            "Volumes EBS não utilizados",
            "Savings Plans disponíveis",
            "S3 sem política de lifecycle"
        ],
        acoes_realizadas=["Exemplo: desligamento automático aplicado"],
        plano_proximo=["Exemplo: ativar política de lifecycle em S3"]
    )
    
    HTML(string=html_out).write_pdf("Relatorio_FinOps.pdf")
    print("✅ PDF gerado: Relatorio_FinOps.pdf")

if __name__ == '__main__':
    dados = obter_dados_cloudcheckr()
    gerar_pdf(dados)
