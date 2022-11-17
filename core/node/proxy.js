const { Client } = require('express-websocket-proxy')
const axios = require("axios")

const proxyClient = new Client('wss://proxy.oyintare.dev/')
const HEADERS_TO_NOT_FORWARD = ['content-length']
async function ProxyRequest(req) {

	try {
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
			req.send(result.data)
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

proxyClient.on('-get|assistant\\/.*|assistant', ProxyRequest)
proxyClient.on('-post|assistant\\/.*', ProxyRequest)
proxyClient.on('-put|assistant\\/.*', ProxyRequest)
proxyClient.on('-delete|assistant\\/.*', ProxyRequest)

proxyClient.connect()