const { Client, WebRequest } = require('express-websocket-proxy')
const axios = require("axios")

const proxyClient = new Client("assistant", 'wss://proxy.oyintare.dev/', true)
const HEADERS_TO_NOT_FORWARD = ['content-length']
async function ProxyRequest(req) {

	try {
		console.log(req.originalUrl)
		const actual_url = `http://localhost:24559${req.originalUrl.substring("/assistant".length)}`

		const headers = Array.from(Object.entries(req.headers)).reduce((obj, [h, v]) => {
			if (!HEADERS_TO_NOT_FORWARD.includes(h.toLowerCase())) {
				obj[h] = v;
			}

			return obj
		}, {})

		axios({
			method: req.method.toLowerCase(),
			url: actual_url,
			data: req.body,
			headers: headers,
			validateStatus: () => true,
		}).then((result) => {
			if (result.data.status) req.status(result.data.status)
			req.send(result.data.body)
			console.log("Sent", req.originalUrl, result.data)
		}).catch((err) => {
			console.log(err)
			req.sendStatus(200)
		})

	}
	catch (err) {
		console.log(err)
		req.sendStatus(200)
	}

}

proxyClient.get('.*', ProxyRequest, true)
proxyClient.post('.*', ProxyRequest, true)
proxyClient.put('.*', ProxyRequest, true)
proxyClient.delete('.*', ProxyRequest, true)

proxyClient.connect()