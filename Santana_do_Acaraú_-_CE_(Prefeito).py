import requests
import streamlit as st
import os
import datetime
import time
from streamlit_extras.stylable_container import stylable_container

st.set_page_config(layout="wide")

# CONSTANTES
host = "resultados.tse.jus.br"
ambiente = "oficial"  # oficial ou simulado
ciclo = "ele2024"
eleicao = "619"  # 1º turno = 619 | 2º turno = 620
estado = "ce"
codigoMunicipio = "15415"  # 15415 para Santana
cargo = "0011"  # 0011 para prefeito | 0013 para vereador
codigoEleicao = f'000{eleicao}'  # alterar quantidade de 0's dependendo do código
arquivo = f'{estado}{codigoMunicipio}-c{cargo}-e{codigoEleicao}-u.json'
arquivo = "ce15415-c0011-e000619-u.json"

# Função para baixar a foto do candidato
def baixar_foto_candidato(host, ambiente, ciclo, eleicao, estado, cargo, sqcand, codigoMunic):
    caminho_foto = f'./fotos_cand_{estado}_{codigoMunic}_{cargo}/{sqcand}.jpeg'
    if not os.path.isdir(f"./fotos_cand_{estado}_{codigoMunic}_{cargo}"):
        os.mkdir(f"./fotos_cand_{estado}_{codigoMunic}_{cargo}")
    if not os.path.isfile(caminho_foto):
        url_foto = f'https://{host}/{ambiente}/{ciclo}/{eleicao}/fotos/{estado}/{sqcand}.jpeg'
        try:
            response = requests.get(url_foto)
            if response.status_code == 200:
                with open(caminho_foto, 'wb') as f:
                    f.write(response.content)
        except Exception as e:
            print(f"Erro ao tentar baixar a foto: {e}")

# Função para exibir informações de cada candidato
def exibir_informacoes_candidato(cargo, nome, numero, posicao, eleito, situacao, votos_validos, percentual_votos, sqcand, codigoMunic):
    # Exibe a imagem do candidato
    cor_borda = "rgba(255, 0, 0, 1)"
    nome_cor_borda = "red"
    if situacao != "Não eleito" and situacao != "":
        if "Eleito" in situacao or "turno" in situacao:
            cor_borda = "rgba(0, 255, 0, 1)"
            nome_cor_borda = "green"

        else:
            cor_borda = "rgba(255, 255, 0, 1)"
            nome_cor_borda = "yellow"
    with stylable_container(
        key=f"container_with_border_{nome_cor_borda}",
        css_styles="""
            {
                border: 2px solid """ + f"{cor_borda}" + """;
                border-radius: 0.5rem;
                padding: calc(1em - 1px)
            }
            """,
    ):
        c = st.container()
        with c:
            col1, col2 = st.columns([0.3, 0.7])
            col1.image(f"./fotos_cand_{estado}_{codigoMunic}_{cargo}/{sqcand}.jpeg", width=130)
            # Exibe as informações do candidato
            col2.markdown(f'''
                       ### {nome} - {numero}\n
                        **Votos Válidos**: {votos_validos} votos ({percentual_votos}%)\n
                        **Situação**: {situacao}''') 
    st.write(f"---")
    print(f"{nome} - {numero} - {votos_validos} - {percentual_votos} - {situacao}")
# Função para processar os dados dos candidatos e gerar as imagens
def processar_dados_candidatos(host, ambiente, ciclo, eleicao, estado, arquivo, codigoMunic):
    url = f'https://{host}/{ambiente}/{ciclo}/{eleicao}/dados/{estado}/{arquivo}'
    url = "https://resultados.tse.jus.br/oficial/ele2024/619/dados/ce/ce15415-c0011-e000619-u.json"
    print(url)
    cargo = "prefeito"
    
    try:
        response = requests.get(url)
        if True:
            dados = response.json()
            data = dados.get("dt", "") if dados.get("dt", "") != "" else dados.get("dg", "")
            hora = dados.get("ht", "") if dados.get("ht", "") != "" else dados.get("hg", "")
            qtd_secoes = dados.get("s", [])
            percent_urna = dados.get("s", {}).get("pst", "")
            votos = dados.get("v", [])
            # Exibe informações gerais da eleição
            st.write(f"##### Atualizado dia {data} às {hora}")
            st.progress(float(percent_urna.replace(",", ".")) / 100, f"**{qtd_secoes['st']} seções apuradas ({percent_urna}%) de {qtd_secoes['ts']} seções totais**")
            st.write()
            col1, col2, col3 = st.columns(3)

            col1.write(f'''🟢 **Votos Válidos: {votos['vv']} votos ({votos['pvv']}%)**''')
            col2.write(f'''⚪ **Votos Brancos: {votos['vb']} votos ({votos['pvb']}%)**''')
            col3.write(f'''⚫ **Votos Nulos: {votos['tvn']} votos ({votos['ptvn']}%)**''')

            st.divider()

            # Extrair a lista de candidatos
            carg = dados.get("carg", [])
            if carg:
                lista_candidatos = []
                agr = carg[0].get("agr", [])

                for a in agr:
                    for p in a.get("par", []):
                        for candidato in p.get("cand", []):
                            lista_candidatos.append(candidato)

                # Ordenar os candidatos por votos válidos (vap) em ordem decrescente
                lista_candidatos.sort(key=lambda x: int(x.get("vap", 0)), reverse=True)


                # Processar cada candidato
                for candidato in lista_candidatos:
                    nome = candidato.get("nmu", "Desconhecido")
                    numero = candidato.get("n", "Desconhecido")
                    posicao = candidato.get("seq", "Desconhecido")
                    eleito = "Sim" if candidato.get("e", "n") == "s" else "Não"
                    situacao = candidato.get("st", "Desconhecida")
                    votos_validos = candidato.get("vap", 0)
                    percentual_votos = candidato.get("pvap", "0%")
                    sqcand = candidato.get("sqcand", "Desconhecido")

                    # Baixar a foto do candidato
                    baixar_foto_candidato(host, ambiente, ciclo, eleicao, estado, cargo, sqcand, codigoMunic)

                    exibir_informacoes_candidato(cargo, nome, numero, posicao, eleito, situacao, votos_validos, percentual_votos, sqcand, codigoMunic)


                    # Gerar a imagem do candidato com todas as informações
                    # gerar_imagem_candidato(percent_urna, data, hora, cargo, nome, numero, posicao, eleito, situacao, votos_validos, percentual_votos, sqcand)

        else:
            st.write(f"Erro na requisição: {response.status_code}")
    except Exception as e:
        st.write(f"Erro ao processar os dados: {e}")

# Função principal da aplicação Streamlit
def main():
    while True:
        st.markdown('''
                    ## Eleições para Prefeito 2024 - Santana do Acaraú - CE
                    ''')
        
        processar_dados_candidatos(host, ambiente, ciclo, eleicao, estado, arquivo, codigoMunicipio)
        time.sleep(60)
        st.rerun()

# Chamar a função principal
if __name__ == '__main__':
    main()
