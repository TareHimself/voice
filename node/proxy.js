const { Client } = require('express-websocket-proxy')
const express = require('express')
const axios = require("axios")

const proxyClient = new Client('wss://proxy.oyintare.dev/')

async function ProxyRequest(req) {
	const result = await axios({
		method: req.method.toLowerCase(),
		url: `http://localhost:24559${req.originalUrl.substring("/assistant".length)}`,
		body: req.body,
		headers: req.headers,
		validateStatus: () => true,
	})

	req.send(result.data)
}

proxyClient.get('assistant/*', ProxyRequest)
proxyClient.post('assistant/*', ProxyRequest)
proxyClient.put('assistant/*', ProxyRequest)
proxyClient.delete('assistant/*', ProxyRequest)

proxyClient.connect()