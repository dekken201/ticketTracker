import json
from bs4 import BeautifulSoup
import re
import os
from .config import *
from datetime import datetime

now = datetime.now()
date = now.strftime("%Y%m%d")

def open_json():
    filePath = os.path.abspath(__file__)
    i = 0
    for i in range(2):
        filePath = os.path.dirname(filePath)
        i += 1
    try:
        with open(filePath+"/output/entradaJson_"+date+".txt") as json_file:
            data = json.load(json_file)
            return data
    except Exception as e:
        return "Erro ao carregar o JSON: "+str(e)

#####get subject####
def getSubject(data):
	items = {}
	for item in data:
		assunto = data[item]['subject']
		try:
			dadosChamado = assunto.split("Chamado nº ")[1]
		except IndexError:
			dadosChamado = assunto.split("Chamadonº")[1]

		numChamado = getNumChamado(dadosChamado)
		situacaoChamado = getSituacaoChamado(dadosChamado)
		pendenciaChamado = getPendenciaChamado(dadosChamado, situacaoChamado == "ABERTURA")

		if any(
			[(numChamado == None), 
			(situacaoChamado == None),
			(pendenciaChamado == None)
			]):
			print("Erro encontrado nos métodos de extração. Fechando o programa.")
			break
		items[item] = {"numChamado":numChamado, 'situacaoChamado':situacaoChamado,
		'pendenciaChamado':pendenciaChamado}
	return items

def getNumChamado(dadosChamado):
	#usar split em vez de regex?
	numChamado = re.findall(r"(\d{5})", dadosChamado)
	try:
		numChamado = numChamado[0]
	except Exception as e:
		print("Erro em getNumChamado - "+str(e))
		return None

	return numChamado

def getSituacaoChamado(dadosChamado):
	try:
		if dadosChamado.count("-") == 1:
			situacaoChamado = (dadosChamado.split("-"))[1].strip()
		elif dadosChamado.count("-") == 2:
			situacaoChamado = (dadosChamado.split("-"))
			situacaoChamado = situacaoChamado[1].strip()
		else:
			print("Erro na contagem dos '-'")
			return None
	except Exception as e:
		print("Erro em getSituacaoChamado - "+str(e))
		return None

	return situacaoChamado

def getPendenciaChamado(dadosChamado, eAbertura):
	try:
		if (eAbertura == True):
			pendenciaChamado = "ATENDENTE"
		else:
			pendenciaChamado = (dadosChamado.split("-"))
			pendenciaChamado = pendenciaChamado[2].strip()
	except Exception as e:
		print("Erro no getPendenciaChamado - "+str(e))
		return None

	return pendenciaChamado


####GET CORPO EMAIL####
def getBody(data):
	items = {}
	espaco = ""+chr(32)+chr(32)+""
	for item in data:
		date = data[item]["date"]
		items[item] = {"data" :date}
		body = data[item]['body']		
		soup = (BeautifulSoup(body,'html.parser')).get_text()
		items[item]["upperBody"] = {"ÁREA DE SUPORTE:" : "","PREVISÃO CONCLUSÃO:" : "",
		"COLABORADOR:" : "", "ATENDENTE:" : "", "ASSUNTO:" : "",
		"DETALHAMENTO:" : ""}
		try:
			splitSoup = soup.split('HISTÓRICO DE RETORNOS')	
			for key in getKeys():
				string = (splitSoup[0].split("CHAMADO Nº")[1])
				startIndex = ((string.upper()).find(key) + len(key))-1
				string = (string[startIndex+1:]).lstrip()
				items[item]["upperBody"][key] = string[:string.index(espaco)]
		except IndexError:
			print("IndexError - getBody")
			pass
		except Exception as e:
			print("Erro em getBody: "+str(e))
			break
		try:
			items[item]["historico"] = splitSoup[1]
		except IndexError:
			print("IndexError - getHistorico - Item "+item)#provavelmente não existe nenhum historico ainda
			pass
		except Exception as e:
			print("Erro em getHistoricoItem: "+str(e))
			pass

	return items

def makeObject(data):
	finalJson = {}
	subject = getSubject(data)
	body = getBody(data)
	try:
		for i in subject:
			for j in body:
				if (i == j):
					print("Criando JSON do item "+i)
					finalJson[i] = {"body":body[j], "subject":subject[i]}
	except Exception as e:
		print("Erro no item : "+str(e)+". Continuando...")

	dumpJson(finalJson)

def dumpJson(data):
    try:
        filePath = os.path.abspath(__file__)
        i = 0
        for i in range(2):
            filePath = os.path.dirname(filePath)
            i += 1
        with open(filePath+"/output/JsonDump_"+date+".txt", "w+") as json_file:
            json.dump(data, json_file)
    except Exception as e:
        print("Erro ao salvar o JSON: "+str(e))

