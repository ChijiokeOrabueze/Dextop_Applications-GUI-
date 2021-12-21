import requests,json


# h = requests_with_caching.get("https://www.googleapis.com/books/v1/volumes?q=young and famous")

class requests_with_caching:
    def __init__(self):
        import requests, json

    def create_cache_key(self, base_url, params_d, private_key=['api_key']):
        alph_keys = sorted(params_d.keys())
        output_string = []
        for key in alph_keys:
            if key not in private_key:
                output_string.append(f'{key}={params_d[key]}')
        return base_url+ "_".join(output_string)


    def _read_file(self, cache_fn):
        with open("permanent_cache.txt", 'r', encoding = "utf-8") as outfile:
            temp_cache = outfile.read()
            file =json.loads(temp_cache)
        return file

    def _write_file(self, cache_f):
        with open ("permanent_cache.txt", 'w') as infile:
            infile.write(cache_f)

    def requestURL(self, base_url, params):
        param_list = []
        for key in params.keys():
            param_list.append(f'{key}={params[key]}')
        temp_param = "&".join(param_list)
        res = base_url + "?" + temp_param.replace(" ", "%20")
        return res

    def get(self, base_url, cache = "permanent_cache.txt", params_d = {}, private_key_to_ignore = ['api_key']):
        request_url = self.requestURL(base_url, params_d) #requests.get(base_url, params_d).url
        print(request_url)
        file_to_search = self._read_file(cache)
        content_to_search = self.create_cache_key(base_url, params_d)
        if content_to_search in file_to_search:
            print("found in permanent cache")
            res = file_to_search[content_to_search]
            request_object = requests.Response()
            request_object._content = str(res).encode("utf-8")
            request_object.status_code = 200
            request_object.url = request_url
            return request_object.text
        else:
            res = requests.get(request_url)
            file_to_search[content_to_search] = res.text
            self._write_file(json.dumps(file_to_search))
            return res.text

# request_with_caching = requests_with_caching()
# req = request_with_caching.get(base_url = "https://www.googleapis.com/books/v1/volumes", params_d = {"q":'young and book+intitle:young and famous+inauthor:susan'})
# req
