import requests
import streamlit as st
import os
import datetime
import time
from streamlit_extras.stylable_container import stylable_container

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
def baixar_foto_candidato(host, ambiente, ciclo, eleicao, estado, cargo, sqcand):
    caminho_foto = f'./fotos_cand/{cargo}/{sqcand}.jpeg'
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
def exibir_informacoes_candidato(cargo, nome, numero, posicao, eleito, situacao, votos_validos, percentual_votos, sqcand):
    # Exibe a imagem do candidato
    cor_borda = "rgba(255, 0, 0, 1)"
    nome_cor_borda = "red"
    if situacao != "Não eleito" and situacao != "":
        if "Eleito" in situacao:
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
            col1, col2 = st.columns([0.2, 0.8])
            col1.image(f'./fotos_cand/{cargo}/{sqcand}.jpeg', width=110)
            # Exibe as informações do candidato
            col2.write(f"### {posicao}º lugar: {nome} (Nº{numero})")
            col2.write(f"**Votos Válidos**: {votos_validos} votos")
            col2.write(f"**Percentual de Votos Válidos**: {percentual_votos}%")
            col2.write(f"**Eleito**: {eleito}")
            col2.write(f"**Situação**: {situacao}") 
    st.write(f"---")
# Função para processar os dados dos candidatos e gerar as imagens
def processar_dados_candidatos(host, ambiente, ciclo, eleicao, estado, arquivo):
    url = f'https://{host}/{ambiente}/{ciclo}/{eleicao}/dados/{estado}/{arquivo}'
    url = "https://raw.githubusercontent.com/pmatheus-dev/tse/refs/heads/main/ce15415-c0011-e000619-u.json"
    cargo = "prefeito" if "0011" in arquivo else "vereador"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            dados = response.json()
            data = dados.get("dg", "")
            hora = dados.get("hg", "")
            percent_urna = dados.get("s", {}).get("pst", "")

            # Exibe informações gerais da eleição
            st.write(f"#### Última atualização: {data} às {hora}")
            st.write(f"**Urnas Apuradas**: {percent_urna}%")
            st.divider()
            # st.write(f"**Cargo**: {cargo.capitalize()}")

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
                    print(nome)
                    numero = candidato.get("n", "Desconhecido")
                    posicao = candidato.get("seq", "Desconhecido")
                    eleito = "Sim" if candidato.get("e", "n") == "s" else "Não"
                    situacao = candidato.get("st", "Desconhecida")
                    votos_validos = candidato.get("vap", 0)
                    percentual_votos = candidato.get("pvap", "0%")
                    sqcand = candidato.get("sqcand", "Desconhecido")

                    # Baixar a foto do candidato
                    baixar_foto_candidato(host, ambiente, ciclo, eleicao, estado, cargo, sqcand)

                    exibir_informacoes_candidato(cargo, nome, numero, posicao, eleito, situacao, votos_validos, percentual_votos, sqcand)


                    # Gerar a imagem do candidato com todas as informações
                    # gerar_imagem_candidato(percent_urna, data, hora, cargo, nome, numero, posicao, eleito, situacao, votos_validos, percentual_votos, sqcand)

        else:
            st.write(f"Erro na requisição: {response.status_code}")
    except Exception as e:
        st.write(f"Erro ao processar os dados: {e}")

# Função principal da aplicação Streamlit
def main():
    while 1 + 1 == 2:
        st.title("Resultados das Eleições para Prefeito - Santana do Acaraú")
        st.write("Acompanhe os resultados atualizados dos candidatos a Prefeito.")
        hoje = datetime.datetime.now()

        st.write(hoje)

        # Botão para o usuário atualizar manualmente
        
        processar_dados_candidatos(host, ambiente, ciclo, eleicao, estado, arquivo)
        time.sleep(3)
        st.rerun()

# Chamar a função principal
if __name__ == '__main__':
    main()
