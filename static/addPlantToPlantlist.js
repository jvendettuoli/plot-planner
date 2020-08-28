'use strict';

console.log('START contentSubfrom.js');

const $addBtn = $('.add-btn');
const $addForm = $('.add-form');

const dataAttrPrimary = 'data-primary';
const dataAttrPrimaryId = 'data-primary-id';
const dataAttrProjectId = 'data-project-id';
const dataAttrSecondary = 'data-secondary';
const dataAttrSecondaryId = 'data-secondary-id';
const listGroupItem = 'list-group-item';
const modalBody = 'modal-body';
const project = 'project';
const projects = 'projects';
const plot = 'plot';
const plots = 'plots';
const plantlist = 'plantlist';
const plantlists = 'plantlists';

async function generateFormOptionHtml(option) {
	return `<option value="${option[0]}">${option[1]}</option>`;
}

async function generateLiItemHtml(secondaryType, listItem) {
	let rmvClass;

	if (secondaryType === plots) {
		rmvClass = 'proj-rmv-plot-btn';
	}
	console.log('inHTMLList', listItem);
	return `<li data-secondary-id=${listItem[0]}><a href="/${secondaryType}/${listItem[0]}">${listItem[1]}</a><button class="btn btn-sm text-danger ${rmvClass}"> <i class="fas fa-times"></i></button></li>`;
}

/* On click of an Add button, it queries database to see what plots are
not yet connected, and displays them in a modal. Primary and secondary
types determine if it is a Project to Plot/Plant list, or Plot to
Plantlist connection. */
$addBtn.on('click', async function(evt) {
	evt.preventDefault();
	console.log('click');
	//
	const primaryType = $(this).attr(dataAttrPrimary);
	const primaryId = $(this).parents(`.${listGroupItem}`).attr(dataAttrPrimaryId);
	const secondaryType = $(this).attr(dataAttrSecondary);

	//Select correct modal form and empty it.
	const $formSelect = $(`.${modalBody}[${dataAttrPrimaryId}='${primaryId}']`).find('select');
	console.log('select', $formSelect);
	$formSelect.empty();

	const secondaryConns = await Query.getConnections(primaryType, primaryId, secondaryType);

	//For each returned option, generate an Html option and append it to form
	secondaryConns.options.forEach(async (option) => {
		console.log('option', option);
		const optionHtml = await generateFormOptionHtml(option);
		console.log(optionHtml);

		$formSelect.append(`${optionHtml}`);
	});
});

$addForm.on('submit', async function(evt) {
	evt.preventDefault();
	const $form = $(this);

	const primaryType = $form.attr(dataAttrPrimary);
	const primaryId = $form.parents(`.${modalBody}`).attr(dataAttrPrimaryId);
	const secondaryType = $form.attr(dataAttrSecondary);

	console.log('######submit');
	console.log('this', $(this));
	const $lists = $(`.${listGroupItem}[${dataAttrPrimaryId}='${primaryId}'][${dataAttrPrimary}='${primaryType}']`);
	console.log(
		'Sselector',
		`.${listGroupItem}[${dataAttrPrimaryId}='${primaryId}'][${dataAttrPrimary}='${primaryType}']`
	);

	console.log('LISTS', $lists);
	let serializedInputs = $form.serializeArray();
	console.log('Serialized', serializedInputs);

	console.log(primaryType, primaryId, secondaryType);
	let $secondaryUl;

	if (primaryType === project && secondaryType === plots) {
		serializedInputs.forEach((element) => {
			if (element.name !== 'csrf_token') {
				Connection.projectAddPlot(primaryId, element.value);
			}
		});
		$secondaryUl = $lists.find('.plot-list');
	}
	else if (primaryType === project && secondaryType === plantlists) {
		serializedInputs.forEach((element) => {
			if (element.name !== 'csrf_token') {
				Connection.projectAddPlantList(primaryId, element.value);
			}
		});
		$secondaryUl = $lists.find('.plantlist-list');
	}
	else if (primaryType === plot && secondaryType === projects) {
		serializedInputs.forEach((element) => {
			if (element.name !== 'csrf_token') {
				Connection.projectAddPlot(element.value, primaryId);
			}
		});
		$secondaryUl = $lists.find('.project-list');
	}
	else if (primaryType === plot && secondaryType === plantlists) {
		serializedInputs.forEach((element) => {
			if (element.name !== 'csrf_token') {
				Connection.plotAddPlantList(primaryId, element.value);
			}
		});
		$secondaryUl = $lists.find('.plantlist-list');
	}
	else if (primaryType === plantlist && secondaryType === projects) {
		serializedInputs.forEach((element) => {
			if (element.name !== 'csrf_token') {
				Connection.projectAddPlantList(element.value, primaryId);
			}
		});
		$secondaryUl = $lists.find('.project-list');
	}
	else if (primaryType === plantlist && secondaryType === plots) {
		serializedInputs.forEach((element) => {
			if (element.name !== 'csrf_token') {
				Connection.plotAddPlantList(element.value, primaryId);
			}
		});
		$secondaryUl = $lists.find('.plot-list');
	}

	const secondaryConns = await Query.getConnections(primaryType, primaryId, secondaryType);

	console.log(secondaryConns);
	console.log('listItems', secondaryConns.list_items);

	console.log('SecondaryList', $secondaryUl);
	$secondaryUl.empty();

	/*Bug in here that results in one of the items not being removed 
	from the options and added to list. Just visual, it still is 
	added to database in code above. */
	secondaryConns.list_items.forEach(async (listItem) => {
		console.log('listItem', listItem);
		const listItemHtml = await generateLiItemHtml(secondaryType, listItem);

		$secondaryUl.append(`${listItemHtml}`);
		$form.find(`option:selected[value='${listItem[0]}']`).remove();
	});
});

$('ul.secondary').on('click', 'button', function(evt) {
	evt.preventDefault();
	console.log('X CLICK');
	console.log($(this));

	const $li = $(this).parent();
	console.log($(this).parent());

	const $list = $li.parent();
	const $addSpan = $list.parent('div').find('span');

	const primaryId = $list.parents(`.${listGroupItem}`).attr(dataAttrPrimaryId);
	const primaryType = $addSpan.attr(dataAttrPrimary);
	const secondaryType = $addSpan.attr(dataAttrSecondary);
	const secondaryId = $li.attr(dataAttrSecondaryId);

	if (primaryType === project && secondaryType === plots) {
		Connection.projectRemovePlot(primaryId, secondaryId);
		$li.remove();
	}
	else if (primaryType === plot && secondaryType === projects) {
		Connection.projectRemovePlot(secondaryId, primaryId);
		$li.remove();
	}
	else if (primaryType === project && secondaryType === plantlists) {
		Connection.projectRemovePlantList(primaryId, secondaryId);
		$li.remove();
	}
	else if (primaryType === plot && secondaryType === plantlists) {
		Connection.plotRemovePlantList(primaryId, secondaryId);
		$li.remove();
	}
	else if (primaryType === plantlist && secondaryType === plots) {
		Connection.plotRemovePlantList(secondaryId, primaryId);
		$li.remove();
	}
	else if (primaryType === plantlist && secondaryType === projects) {
		Connection.projectRemovePlantList(secondaryId, primaryId);
		$li.remove();
	}
});
