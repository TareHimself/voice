
const axios = require("axios")
const actual_url = `http://127.1.0.0:24559/telegram/webhook`

axios({
	method: 'post',
	url: actual_url,
	body: undefined,
	headers: null,
	validateStatus: () => true,
}).then((response) => {
	console.log('REQUEST RESULT ', response.data)
})