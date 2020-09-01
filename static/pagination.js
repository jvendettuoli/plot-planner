'use strict';

console.log('START pagination.js');

const $pageFirstLink = $('#page-first').children('a');
const $pagePrevLink = $('#page-prev').children('a');
const $pageNextLink = $('#page-next').children('a');
const $pageLastLink = $('#page-last').children('a');

//Handles requests to server database query endpoints
class Pagination {
	constructor() {
		//Change out based on deployment
		this.baseURL = 'http://127.0.0.1:5000';
	}
	//Change out based on deployment
	static baseUrl = 'http://127.0.0.1:5000';

	//POST request to provide the pagination link
	static async postLink(paginationLink) {
		console.log(paginationLink);

		const res = await axios.post(`${this.baseUrl}/api/plants/pagination`, { pagination_link: paginationLink });

		console.log(res);
		console.log(res.data);

		let plantList = [];
		for (let item of res.data[0]) {
			plantList.push(await Search.extractPlantData(item));
		}
		const links = res.data[1];
		// console.log('plantList', plantList);

		await Search.populateTable(plantList);
		await this.updateLinks(links);
	}

	static async updateLinks(links) {
		$pageFirstLink.attr('data-page', links.first);
		$pagePrevLink.attr('data-page', links.prev);

		$pageNextLink.attr('data-page', links.next);
		$pageLastLink.attr('data-page', links.last);

		if (!('next' in links)) {
			$pageNextLink.parent('li').addClass('disabled');
			$pageLastLink.parent('li').addClass('disabled');
		}
		if (!('prev' in links)) {
			$pageFirstLink.parent('li').addClass('disabled');
			$pagePrevLink.parent('li').addClass('disabled');
		}
		if ('next' in links) {
			$pageNextLink.parent('li').removeClass('disabled');
			$pageLastLink.parent('li').removeClass('disabled');
		}
		if ('prev' in links) {
			$pageFirstLink.parent('li').removeClass('disabled');
			$pagePrevLink.parent('li').removeClass('disabled');
		}
	}
}

$('.page-link').click(function(evt) {
	evt.preventDefault();
	const $pageItem = $(evt.currentTarget);
	console.log($pageItem);
	const isDisabled = $pageItem.hasClass('disabled');
	if (!isDisabled) {
		const paginationLink = $pageItem.attr('data-page');
		console.log(paginationLink);

		Pagination.postLink(paginationLink);
	}
});
