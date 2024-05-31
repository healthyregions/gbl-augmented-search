import json
import http.client
from urllib.parse import urlencode, urlparse
import os
import traceback
import gzip

import re

import nltk
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.corpus import wordnet as wn

print('INFO: Loading SDOH Search!')

# Set NLTK data path to /tmp
nltk.data.path.append("/tmp")
print(f"INFO: Downloading NLTK Packages")
# Download the necessary NLTK datasets into /tmp
nltk.download('stopwords', download_dir='/tmp')
nltk.download('averaged_perceptron_tagger', download_dir='/tmp')
nltk.download('punkt', download_dir='/tmp')
nltk.download('wordnet', download_dir='/tmp')
print(f"INFO: Downloaded NLTK Packages")


API_BASE = os.getenv('API_BASE')
SOLR_URL = os.getenv('SOLR_URL')
SOLR_BASE = os.getenv('SOLR_BASE')

print(API_BASE, SOLR_URL, SOLR_BASE)

class Query:

	def __init__(self):
		pass

	def get_query_expansion(self, query):
		expanded = dict()

		for word in query.split(" "):
			tokens = Synonyms().generate_tokens(word)
			for token in tokens.keys():
				expanded[token] = expanded.get(token, 0)
				expanded[token] += tokens[token]
		expanded = dict(sorted(expanded.items(), key=lambda item: -item[1]))
		print(expanded)
		for q in query.split(" "):
			expanded[q] = 1
		rtn = " ".join(list(expanded.keys()))
		print(rtn)
		return rtn


class Synonyms:

	def __init__(self):
		self.pos_tag_map = {
			'NN': [wn.NOUN],
			'JJ': [wn.ADJ, wn.ADJ_SAT],
			'RB': [wn.ADV],
			'VB': [wn.VERB]
		}

	def pos_tag_converter(self, nltk_pos_tag):
		root_tag = nltk_pos_tag[0:2]
		try:
			self.pos_tag_map[root_tag]
			return self.pos_tag_map[root_tag]
		except KeyError:
			return ''

	def tokenizer(self, sentence):
		return word_tokenize(sentence)

	def pos_tagger(self, tokens):
		return nltk.pos_tag(tokens)

	def stopword_treatment(self, tokens):
		stopword = stopwords.words('english')
		result = []
		for token in tokens:
			if token[0].lower() not in stopword:
				result.append(tuple([token[0].lower(), token[1]]))
		return result

	def get_synsets(self, tokens):
		synsets = []
		for token in tokens:
			wn_pos_tag = self.pos_tag_converter(token[1])
			if wn_pos_tag == '':
				continue
			else:
				synsets.append(wn.synsets(token[0], wn_pos_tag))
		return synsets

	def get_tokens_from_synsets(self, synsets):
		tokens = {}
		for synset in synsets:
			for s in synset:
				if s.name() in tokens:
					tokens[s.name().split('.')[0]] += 1
				else:
					tokens[s.name().split('.')[0]] = 1
		return tokens

	def get_hypernyms(self, synsets):
		hypernyms = []
		for synset in synsets:
			for s in synset:
				hypernyms.append(s.hypernyms())

		return hypernyms

	def get_tokens_from_hypernyms(self, synsets):
		tokens = {}
		for s in synsets:
			for ss in s:
				if ss.name().split('.')[0] in tokens:
					tokens[(ss.name().split('.')[0])] += 1
				else:
					tokens[(ss.name().split('.')[0])] = 1
		return tokens

	def underscore_replacer(self, tokens):
		new_tokens = {}
		for key in tokens.keys():
			mod_key = re.sub(r'_', ' ', key)
			new_tokens[mod_key] = tokens[key]
		return new_tokens

	def generate_tokens(self, sentence):
		tokens = self.tokenizer(sentence)
		tokens = self.pos_tagger(tokens)
		tokens = self.stopword_treatment(tokens)
		synsets = self.get_synsets(tokens)
		synonyms = self.get_tokens_from_synsets(synsets)
		synonyms = self.underscore_replacer(synonyms)
		hypernyms = self.get_hypernyms(synsets)
		hypernyms = self.get_tokens_from_hypernyms(hypernyms)
		hypernyms = self.underscore_replacer(hypernyms)
		tokens = {**synonyms, **hypernyms}
		return tokens


# Create a function to handle the GET request using http.client
def get_response(url, headers, params):
	headers['Accept-Encoding'] = 'gzip'
	url_parts = urlparse(url)
	connection = http.client.HTTPConnection(url_parts.netloc)
	query_string = urlencode(params)
	target = f"{url_parts.path}?{query_string}" if params else url_parts.path
	connection.request("GET", target, headers=headers)
	response = connection.getresponse()
	data = response.read()
	## add handling for non-gzip response
	try:
		results = gzip.decompress(data)
		return json.loads(results.decode())
	except Exception as e:
		results = data.decode()
		return json.loads(results)

# Function to handle the POST request
def post_response(url, headers, params, data):
	url_parts = urlparse(url)
	connection = http.client.HTTPConnection(url_parts.netloc)
	target = url_parts.path
	headers['Content-Type'] = 'application/json'  # Setting Content-Type header for JSON data
	connection.request("POST", target, body=json.dumps(data), headers=headers)
	response = connection.getresponse()
	data = gzip.decompress(response.read())
	return json.loads(data.decode())


# Function to handle the PUT request
def put_response(url, headers, params, data):
	url_parts = urlparse(url)
	connection = http.client.HTTPConnection(url_parts.netloc)
	target = url_parts.path
	headers['Content-Type'] = 'application/json'  # Setting Content-Type header for JSON data
	connection.request("PUT", target, body=json.dumps(data), headers=headers)
	response = connection.getresponse()
	data = gzip.decompress(response.read())
	return json.loads(data.decode())


# Function to handle the DELETE request
def delete_response(url, headers, params):
	url_parts = urlparse(url)
	connection = http.client.HTTPConnection(url_parts.netloc)
	query_string = urlencode(params)
	target = f"{url_parts.path}?{query_string}" if params else url_parts.path
	connection.request("DELETE", target, headers=headers)
	response = connection.getresponse()
	data = gzip.decompress(response.read())
	return json.loads(data.decode())


def respond(err, res=None):
	return {
		'statusCode': '400' if err else '200',
		'body': str(err) if err else json.dumps(res),
		'headers': {
			'Content-Type': 'application/json',
			"Access-Control-Allow-Origin": "*", 
			"Access-Control-Allow-Methods": "GET, POST, DELETE, PUT", 
			"Access-Control-Allow-Headers": "Content-Type, Authorization" 
		},
	}


def handle_get(dynamic_route, headers, params):
	if params and params.get("q"):
		dynamic_route = "search"
		params["df"] = "text"
		query = Query()
		params["q"] = query.get_query_expansion(params["q"])

	url = f"{SOLR_URL}{SOLR_BASE}{dynamic_route}"
	response = get_response(url, headers, params)
	return response


def handle_post(dynamic_route, headers, params, data):
	url = f"{SOLR_URL}{SOLR_BASE}{dynamic_route}"
	response = post_response(url, headers, params, data)
	return response


def handle_put(dynamic_route, headers, params, data):
	url = f"{SOLR_URL}{SOLR_BASE}{dynamic_route}"
	response = put_response(url, headers, params, data)
	return response


def handle_delete(dynamic_route, headers, params):
	url = f"{SOLR_URL}{SOLR_BASE}{dynamic_route}"
	response = delete_response(url, headers, params)
	return response


def lambda_handler(event, context):
	headers = event['headers']
	params = event['queryStringParameters']
	dynamic_route = event["path"].replace(API_BASE, "")
	operation = event['httpMethod']

	operations = {
		'GET': handle_get,
		'POST': handle_post,
		'PUT': handle_put,
		'DELETE': handle_delete
	}

	if operation in operations:
		if operation == "GET":
			try:
				data = operations[operation](dynamic_route, headers, params)
			except Exception as e:
				print(e)
				traceback.print_exc()
				return respond(e, None)
			return respond(None, data)
		elif operation == "POST":
			try:
				payload = None
				data = operations[operation](dynamic_route, headers, params, payload)
			except Exception as e:
				print(e)
				traceback.print_exc()
				return respond(e, None)
			return respond(None, data)
		elif operation == "PUT":
			try:
				payload = None
				data = operations[operation](dynamic_route, headers, params, payload)
			except Exception as e:
				print(e)
				traceback.print_exc()
				return respond(e, None)
			return respond(None, data)
		elif operation == "DELETE":
			try:
				data = operations[operation](dynamic_route, headers, params)
			except Exception as e:
				print(e)
				traceback.print_exc()
				return respond(e, None)
			return respond(None, data)
	else:
		return respond(ValueError('Unsupported method "{}"'.format(operation)))
