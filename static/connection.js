'use strict';

/*
Connection Class handles when various components add or remove other components. Currently more set up for organizational purposes than
actual use of instances.
*/
class Connection {
	constructor() {
		//Change out based on deployment
		this.baseURL = 'https://plot-planner.herokuapp.com';
	}
	//Change out based on deployment
	static baseUrl = 'https://plot-planner.herokuapp.com';

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
	//POST request to add symbol to a plot cell
	static async plotCellAddSymbol(plotId, cellX, cellY, plantlistsPlantsId) {
		const res = await axios.post(
			`${this.baseUrl}/plots/${plotId}/add/symbol/${plantlistsPlantsId}/x/${cellX}/y/${cellY}`
		);
	}
	//POST request to delete symbol from a plot cell
	static async plotCellDeleteSymbol(plotId, cellX, cellY) {
		const res = await axios.post(`${this.baseUrl}/plots/${plotId}/delete/cell/x/${cellX}/y/${cellY}`);
	}
}
