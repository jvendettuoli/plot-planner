'use strict';

console.log('START changeConnection.js');

class Connection {
	constructor() {
		//Change out based on deployment
		this.baseURL = 'http://127.0.0.1:5000';
		// this.projectId = projectId;
		// this.plotId = plotId;
	}
	//Change out based on deployment
	static baseUrl = 'http://127.0.0.1:5000';

	//POST request to remove plot from project
	static async projectRemovePlot(projectId, plotId) {
		const res = await axios.post(`${this.baseUrl}/projects/${projectId}/remove/plot/${plotId}`);
	}
	//POST request to remove plant list from project
	static async projectRemovePlantList(projectId, plantlistId) {
		const res = await axios.post(`${this.baseUrl}/projects/${projectId}/remove/plantlist/${plantlistId}`);
	}
	//POST request to remove plant list from plot
	static async plotRemovePlantList(plotId, plantlistId) {
		const res = await axios.post(`${this.baseUrl}/plots/${plotId}/remove/plantlist/${plantlistId}`);
	}
	//POST request to add plant list to plot
	static async plotAddPlantList(plotId, plantlistId) {
		const res = await axios.post(`${this.baseUrl}/plots/${plotId}/add/plantlist/${plantlistId}`);
	}
	//POST request to add plant list to project
	static async projectAddPlantList(projectId, plantlistId) {
		const res = await axios.post(`${this.baseUrl}/projects/${projectId}/add/plantlist/${plantlistId}`);
	}
	//POST request to add plot to project
	static async projectAddPlot(projectId, plotId) {
		const res = await axios.post(`${this.baseUrl}/projects/${projectId}/add/plot/${plotId}`);
	}
}
