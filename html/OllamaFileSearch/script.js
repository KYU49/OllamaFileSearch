{
	
PHP_ADDRESS = "./sseEndpoint.php"
class SearchModel {
	constructor() {
		this.defaultTitle = "Mumblore";
		this.searchTitle = "検索結果";
		this.searchResults = [];
		this.llmOutput = '';
		this.labels = [];
		this.labelsSelected = [];
		this.searchEnabled = true;
	}

	// サーバーからラベルリストを取得
	async loadLabels() {
		try {
			const response = await fetch(".config/labelList.yaml"); // YAMLファイルを取得
			const text = await response.text(); // ファイルの内容をテキストとして取得

			// YAMLをパースするために簡単に手動で処理
			const labelList = this.parseYAML(text);

			// ラベルをセット
			this.labels = labelList || [];
			this.labelsSelected = this.labels.map(() => false);
		} catch (error) {
			console.error("ラベルの読み込み中にエラーが発生しました:", error);
		}
	}

	// YAMLの簡易パース（手動）
	parseYAML(yamlText) {
		// 改行で分けて、キーと値をセット
		const lines = yamlText.split('\n');
		const labelList = [];

		// 行ごとに処理
		lines.forEach(line => {
			line = line.trim();
			if (line.startsWith('- ')) {
				labelList.push(line.substring(2).trim());
			}
		});
		return labelList;
	}
	
	setSearchResults(results) {
		this.searchResults = results;
	}

	appendLlmOutput(token) {
		this.llmOutput += token;
	}

	clear() {
		this.searchResults.splice(0);
		this.llmOutput = '';
	}
}

// View
class SearchView {
	constructor() {
		this.searchResultsDiv = document.getElementById("searchResults");
		this.labelContainer = document.getElementById("labelContainer");
		this.llmOutputDiv = document.getElementById("llmOutput");
		this.titleSpan = document.getElementById("title");
		this.backBtn = document.getElementById("backBtn");
		this.chatInput = document.getElementById("chatInput");
		this.searchBtn = document.getElementById("searchBtn");
		this.labelViews = [];
		this.loadingView = document.getElementById("loading");
		this.loadingView.classList.add("hidden");
		this.userQuestion = document.getElementById("userQuestion");
	}

	drawLabel(labels){
		// ラベルボタン
		labels.forEach(label => {
			const btn = document.createElement("span");
			btn.textContent = "#" + label;
			btn.className = "label-button";
			btn.addEventListener("click", (e) => {
				this.onLabelClick(e, label);
			});
			this.labelViews.push(btn);
			this.labelContainer.appendChild(btn);
		});
	}

	updateSearchResults(searchResults) {
		this.searchResultsDiv.innerHTML = "";
		const alreadyAdded = [];
		// 検索結果リスト
		searchResults.forEach(r => {
			if(!alreadyAdded.includes(r.metadata.source)){
				const item = document.createElement("div");
				item.className = "result-item";
				item.dataset.label = r.metadata.label;
				const source = document.createElement("a");
				source.innerText = r.metadata.source;
				source.href = r.metadata.source;
				source.target = "_blank";
				const description = document.createElement("div");
				description.innerText = r.metadata.description;
				item.appendChild(source);
				item.appendChild(description);
				this.searchResultsDiv.appendChild(item);
				alreadyAdded.push(r.metadata.source);
			}
		});
	}

	updateLlmOutput(output) {
		this.llmOutputDiv.innerHTML = output.replace(/\r?\n/g, "");
	}

	setTitle(title) {
		this.titleSpan.textContent = title;
	}

	showBackButton() {
		this.backBtn.style.display = "inline-block";
	}

	hideBackButton() {
		this.backBtn.style.display = "none";
	}

	clearSearchResults() {
		this.searchResultsDiv.innerHTML = "";
		this.llmOutputDiv.innerHTML = "";
		this.userQuestion.innerText = "";
	}

	onLabelClick(e, label) {
		// ViewModelにラベルでフィルタをかけるリクエスト
		this.viewModel.filterByLabel(label);
		e.currentTarget.classList.toggle("active", this.viewModel.isLabelSelected(label));
	}

	searchStart(isStart, userQuestion=""){
		if(userQuestion){
			this.userQuestion.innerText = "> " + userQuestion;
		}
		this.searchBtn.disabled = isStart;
		this.loadingView.classList.toggle("hidden", !isStart);
	}

	bindSearch(handler) {
		this.chatInput.addEventListener("keydown", (e) => {
			if (e.key === "Enter") handler();
		});
		this.searchBtn.addEventListener("click", handler);
	}

	bindBack(handler) {
		this.backBtn.addEventListener("click", handler);
	}
}

// ViewModel
class SearchViewModel {
	constructor(model, view) {
		this.model = model;
		this.view = view;

		// バインディング
		this.view.viewModel = this;
		this.view.bindSearch(() => this.startSearch());
		this.view.bindBack(() => this.resetSearch());
	}

	startSearch() {
		const prompt = this.view.chatInput.value.trim();
		if (!prompt) return;
		
		if(!this.model.searchEnabled){
			return;
		}
		this.model.searchEnabled = false;

		// 初期化
		this.view.clearSearchResults();
		this.model.clear();

		this.view.searchStart(true, prompt);

		this.view.setTitle(this.model.searchTitle);
		this.view.showBackButton();
		
		if(this.model.labels.length == 0){
			// labelを描画
			this.model.loadLabels().then(() => {
				this.view.drawLabel(this.model.labels);
			});
		}

		// SSE接続
		const evtSource = new EventSource(PHP_ADDRESS + "?prompt=" + encodeURIComponent(prompt), { withCredentials: false });

		evtSource.addEventListener("search", (e) => {
			const data = JSON.parse(e.data);
			this.model.setSearchResults(data);
			this.view.updateSearchResults(this.model.searchResults);
		});

		evtSource.addEventListener("answer_token", (e) => {
			if(e.data === "[DONE]") {
				this.model.searchEnabled = true;
				this.view.searchStart(false);
				return;
			}
			const data = JSON.parse(e.data);
			if (data.token) {
				this.model.appendLlmOutput(data.token);
				this.view.updateLlmOutput(this.model.llmOutput);
			}
		});

		evtSource.addEventListener("end", () => {
			evtSource.close();
		});

		this.view.chatInput.value = "";
	}

	resetSearch() {
		this.view.setTitle(this.model.defaultTitle);
		this.view.hideBackButton();
		this.view.clearSearchResults();
		this.model.clear();
	}

	filterByLabel(label) {
		const selected = this.model.labels.indexOf(label);
		this.model.labelsSelected[selected] = !this.model.labelsSelected[selected];
		document.querySelectorAll(".result-item").forEach(item => {
			let visible = this.model.labelsSelected[this.model.labels.indexOf(item.dataset.label)];
			item.classList.toggle("hidden", !visible);
			if(this.model.labelsSelected.every(value => !value)){
				item.classList.toggle("hidden", false);
			}
		});
	}
	isLabelSelected(label) {
		return this.model.labelsSelected[
			this.model.labels.indexOf(label)
		];
	}
}

window.onload = () => {
// 初期化
	const model = new SearchModel();
	const view = new SearchView();
	const viewModel = new SearchViewModel(model, view);
}

}