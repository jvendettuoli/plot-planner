'use strict';

console.log('START query.js');

//Handles requests to server database query endpoints
class Query {
	constructor() {
		//Change out based on deployment
		this.baseURL = 'http://127.0.0.1:5000';
	}
	//Change out based on deployment
	static baseUrl = 'http://127.0.0.1:5000';

	//GET request to get connections based on a primaryId and secondary type
	static async getConnections(primaryType, primaryId, secondaryType) {
		const res = await axios.get(`${this.baseUrl}/query/${primaryType}/${primaryId}/${secondaryType}`);

		return res.data;
	}
}