const { Client } = require('express-websocket-proxy')
const express = require('express')
const axios = require("axios")

const proxyClient = new Client('wss://proxy.oyintare.dev/')

async function ProxyRequest(req) {

	try {
		const actual_url = `http://127.1.0.0:24559${req.originalUrl.substring("/assistant".length)}`

		axios({
			method: req.method.toLowerCase(),
			url: actual_url,
			body: req.body,
			headers: req.headers,
			validateStatus: () => true,
		}).then((result) => {
			console.log('REQUEST RESULT ', result.data)
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