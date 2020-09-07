'use strict';

//Pagination button links
const $pageFirstLink = $('#page-first').children('a');
const $pagePrevLink = $('#page-prev').children('a');
const $pageNextLink = $('#page-next').children('a');
const $pageLastLink = $('#page-last').children('a');

// When pagination button is clicked, show the next set of plants
$('.page-link').click(handlePagination);

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
		const res = await axios.post(`${this.baseUrl}/api/plants/pagination`, { pagination_link: paginationLink });

		let plantList = [];
		for (let item of res.data[0]) {
			plantList.push(await Search.extractPlantData(item));
		}
		const links = res.data[1];

		//Populate table with new plant data and update pagination links
		await Search.populateTable(plantList);
		await this.updateLinks(links);
	}

	//Update pagination links
	static async updateLinks(links) {
		$pageFirstLink.attr('data-page', links.first);
		$pagePrevLink.attr('data-page', links.prev);
		$pageNextLink.attr('data-page', links.next);
		$pageLastLink.attr('data-page', links.last);

		// Trefle returns pagination links with next and prev only if
		// there is a next or previous page, so we use this to change
		// the style of the buttons and disable them when applicable
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

// checks if link is disabled, and if not loads the next set of plants
// and updates pagination links
function handlePagination(evt) {
	evt.preventDefault();
	const $pageItem = $(evt.currentTarget);
	const isDisabled = $pageItem.hasClass('disabled');
	if (!isDisabled) {
		const paginationLink = $pageItem.attr('data-page');
		Pagination.postLink(paginationLink);
	}
}
