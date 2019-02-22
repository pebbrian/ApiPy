import json

import requests


class API_Manager:
	"""
		Vérifie que les requêtes formulées respectent bien une norme d'API donnée avant de les envoyer
		ver: 190114
	"""

	def __init__(self, def_path: (list, tuple)):
		"""
			Constructeur : charge et stocke la définition de l'API si elle est correcte.
			Lance une erreur spécifique le cas contraire.
		"""
		self.API_list = []

		for path in def_path:
			with open(path) as file:
				api_def = json.load(file)
				self.check_def(api_def)
				self.API_list.append(api_def)

		self.selected_API = None

	@staticmethod
	def check_def(api_def):
		"""
			Vérifie que la définition soit correcte.
			Lance une erreur spécifique le cas contraire.
		"""
		if not 'url' or 'requests' not in api_def:
			raise ValueError('"url" and/or "requests" key missing in API definition')

	@staticmethod
	def check_required_params(params: dict, payload: dict):
		"""
			Vérifie que la paramètres requis soient bien présents dans la charge utile.
			Lance une erreur spécifique le cas contraire.
		"""
		for par in params:
			if 'required' in params[par]:
				if params[par]['required']:
					if par not in payload:
						raise ValueError('Required argument not provided : ' + par)

	@staticmethod
	def check_unknow_params(params: dict, payload: dict):
		"""
			Vérifie que les paramètres soient présents dans la définition.
			Lance une erreur spécifique le cas contraire.
		"""
		for par in payload:
			if par not in params:
				raise ValueError('Unknow parameter : ' + par)

	@staticmethod
	def check_params_values(params: dict, payload: dict):
		"""
			Vérifie que les valeurs des paramètres de la charge utile possèdent bien des valeurs acceptées.
			Lance une erreur spécifique le cas contraire.
		"""
		for par in payload:
			if par in params:
				if 'values' in par:
					if payload[par] not in par['values']:
						raise ValueError('Unknow parameter : ' + par)

	@staticmethod
	def add_default_params(params: dict, payload: dict):
		"""
			Ajoute les paramètres par défaut à la charge utile et retourne le résultat.
		"""
		_dict = {}
		for key in params:
			if 'value' in params[key]:
				_dict.update({key: params[key]['value']})
		_dict.update(payload)
		return _dict

	def get_url(self):
		"""
			Retourne l'URL de l'API d'après sa définition.
		"""
		return self.selected_API['url']

	def get_name(self):
		"""
			Retourne le nom de l'API d'après sa définition.
		"""
		return self.selected_API['name']

	def get_caller(self, request):
		"""
			Retourne le caller de l'API d'après sa définition.
		"""
		return self.selected_API['requests'][request]['caller']

	def get_params(self, request):
		"""
			Retourne la liste des paramètres de la requête relative à l'API d'après sa définition
		"""
		return {key_param: value_param for key_param, value_param in self.selected_API['requests'][request] if key_param != 'caller'}

	def check_request(self, request):
		"""
			Vérifie que la requête soit présente dans la définition.
			Lance une erreur spécifique le cas échéant.
		"""
		if request not in self.selected_API['requests']:
			raise ValueError('Unknow request : ' + request)

	def complete_payload(self, request: str, payload: dict):
		"""
			Ajoute les paramètres fournis par défaut à la charge utile
		"""
		return self.add_default_params(self.get_params(request), payload)

	def check_params(self, params: dict, payload: dict = None):
		"""
			Vérifie que la requête soit correcte.
			Lance une erreur spécifique le cas échéant.
		"""
		if payload is None:
			payload = {}

		self.check_unknow_params(params, payload)  # Validation : Tous les paramètres sont reconnus
		self.check_required_params(params, payload)  # Validation : Tous les paramètres requis sont présents
		self.check_params_values(params, payload)  # Validation : Les valeurs spécifiées pour les paramètres sont acceptées

	def get(self, request: str, payload: dict = None):
		"""
			Lance une requête GET en accord avec la définition de l'API
			et retourne le résultat ou lance une erreur le cas échéant.
		"""
		if payload is None:
			payload = {}

		for i, api in enumerate(self.API_list, start=1):
			self.selected_API = api

			try:
				self.check_request(request)
				payload = self.complete_payload(request, payload)
				params = self.get_params(request)
				self.check_params(params, payload)

				res = requests.get(self.get_url() + '/' + self.get_caller(request), payload)
				if res.status_code == 200:
					return self.get_name(), res.json()
				elif i == len(self.API_list):
					return None
			except ValueError as e:
				if i <= len(self.API_list) - 1:
					continue
				else:
					raise ValueError(e)
