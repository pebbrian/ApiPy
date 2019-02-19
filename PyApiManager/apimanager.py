import json, requests


class API_Manager:
    """
        Vérifie que les requêtes formulées respectent bien une norme d'API donnée avant de les envoyer
        ver: 190114
    """

    def __init__(self, def_path: str):
        """
            Constructeur : charge et stocke la définition de l'API si elle est correcte.
            Lance une erreur spécifique le cas contraire.
        """
        self.API_list = []

        for path in def_path:
            with open(path) as file:
                API_def = json.load(file)
                self.check_def(API_def)
                self.API_list.append(API_def)

        self.selected_API = None

    def check_def(self, API_def):
        """
            Vérifie que la définition soit correcte.
            Lance une erreur spécifique le cas contraire.
        """
        if not 'url' or not 'requests' in API_def:
            raise Exception('"url" and/or "requests" key missing in API definition')

    def check_required_params(self, params: dict, payload: dict):
        """
            Vérifie que la paramètres requis soient bien présents dans la charge utile.
            Lance une erreur spécifique le cas contraire.
        """
        for par in params:
            if 'required' in params[par]:
                if params[par]['required']:
                    if not par in payload:
                        raise Exception('Required argument not provided : ' + par)

    def check_unknow_params(self, params: dict, payload: dict):
        """
            Vérifie que les paramètres soient présents dans la définition.
            Lance une erreur spécifique le cas contraire.
        """
        for par in payload:
            if not par in params:
                raise Exception('Unknow parameter : ' + par)

    def check_params_values(self, params: dict, payload: dict):
        """
            Vérifie que les valeurs des paramètres de la charge utile possèdent bien des valeurs acceptées.
            Lance une erreur spécifique le cas contraire.
        """
        for par in payload:
            if par in params:
                if 'values' in par:
                    if payload[par] not in par['values']:
                        raise Exception('Unknow parameter : ' + par)

    def add_default_params(self, params: dict, payload: dict):
        """
            Ajoute les paramètres par défaut à la charge utile et retourne le résultat.
        """
        for par in params:
            if 'value' in params[par]:
                return {**payload, **{par: params[par]['value']}}

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
        return self.selected_API[request]['caller']

    def get_params(self, request):
        """
            Retourne la liste des paramètres de la requête relative à l'API d'après sa définition
        """
        return self.selected_API['requests'][request]

    def check_request(self, request):
        """
            Vérifie que la requête soit présente dans la définition.
            Lance une erreur spécifique le cas échéant.
        """
        if not request in self.selected_API['requests']:
            raise Exception('Unknow request : ' + request)

    def complete_payload(self, request: str, payload: dict):
        """
            Ajoute les paramètres fournis par défaut à la charge utile
        """
        return self.add_default_params(self.get_params(request), payload)

    def check_params(self, params: dict, payload: dict = {}):
        """
            Vérifie que la requête soit correcte.
            Lance une erreur spécifique le cas échéant.
        """
        self.check_unknow_params(params, payload)  # Validation : Tous les paramètres sont reconnus
        self.check_required_params(params, payload)  # Validation : Tous les paramètres requis sont présents
        self.check_params_values(params, payload)  # Validation : Les valeurs spécifiées pour les paramètres sont acceptées

    def get(self, request: str, payload: dict = {}):
        """
            Lance une requête GET en accord avec la définition de l'API
            et retourne le résultat ou lance une erreur le cas échéant.
        """
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
            except Exception:
                if i <= len(self.API_list) - 1:
                    continue
                else:
                    return None
