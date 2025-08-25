{
	
PHP_ADDRESS = "../sseEndpoint.php"
class SearchModel {
	constructor() {
		this.defaultTitle = "Mumblore";
		this.searchTitle = "検索結果";
		this.searchResults = [];
		this.llmOutput = '';
		this.labels = [];
		this.loadLabels();
	}

	// サーバーからラベルリストを取得
	async loadLabels() {
		try {
			const response = await fetch("../.config/labelList.yaml"); // YAMLファイルを取得
			const text = await response.text(); // ファイルの内容をテキストとして取得

			// YAMLをパースするために簡単に手動で処理
			const labelList = this.parseYAML(text);

			// ラベルをセット
			this.labels = labelList || [];
			console.log("Labels:", this.labels);
		} catch (error) {
			console.error("ラベルの読み込み中にエラーが発生しました:", error);
		}
	}

	// YAMLの簡易パース（手動）
	parseYAML(yamlText) {
		// 改行で分けて、キーと値をセット
		const lines = yamlText.split('\n');
		const labelList = [];
		let isLabelList = false;

		// 行ごとに処理
		lines.forEach(line => {
			line = line.trim();
			if (line.startsWith('labelList:')) {
				isLabelList = true; // labelListが始まったらフラグを立てる
			} else if (isLabelList && line.startsWith('- ')) {
				// ラベルのリストを追加
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
		this.searchResults = [];
		this.llmOutput = '';
		this.labels = [];
	}
}

// View
class SearchView {
	constructor() {
		this.searchResultsDiv = document.getElementById("searchResults");
		this.llmOutputDiv = document.getElementById("llmOutput");
		this.titleSpan = document.getElementById("title");
		this.backBtn = document.getElementById("backBtn");
		this.chatInput = document.getElementById("chatInput");
		this.searchBtn = document.getElementById("searchBtn");
	}

	updateSearchResults(results) {
		this.searchResultsDiv.innerHTML = "";

		// ラベルボタン
		const labelContainer = document.createElement("div");
		results.labels.forEach(label => {
			const btn = document.createElement("span");
			btn.textContent = "#" + label;
			btn.className = "label-button";
			btn.addEventListener("click", () => {
				this.onLabelClick(label);
			});
			labelContainer.appendChild(btn);
		});
		this.searchResultsDiv.appendChild(labelContainer);

		// 検索結果リスト
		results.searchResults.forEach(r => {
			const item = document.createElement("div");
			item.className = "result-item";
			item.dataset.label = r.metadata.label;
			item.innerHTML = `<strong>${r.metadata.source}</strong><br>${r.metadata.description}`;
			this.searchResultsDiv.appendChild(item);
		});
	}

	updateLlmOutput(output) {
		this.llmOutputDiv.textContent = output;
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
	}

	onLabelClick(label) {
		// ViewModelにラベルでフィルタをかけるリクエスト
		this.viewModel.filterByLabel(label);
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

		// 初期化
		this.view.clearSearchResults();
		this.view.setTitle(this.model.searchTitle);
		this.view.showBackButton();

		// SSE接続
		const evtSource = new EventSource(PHP_ADDRESS + "?prompt=" + encodeURIComponent(prompt), { withCredentials: false });

		evtSource.addEventListener("search", (e) => {
			const data = JSON.parse(e.data);
			this.model.setSearchResults(data.search_results);
			this.view.updateSearchResults(this.model);
		});

		evtSource.addEventListener("answer_token", (e) => {
			if(e.data === "[DONE]") {
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
		document.querySelectorAll(".result-item").forEach(item => {
			item.classList.toggle("hidden", item.dataset.label !== label);
		});
	}
}

window.onload = () => {
// 初期化
	const model = new SearchModel();
	const view = new SearchView();
	const viewModel = new SearchViewModel(model, view);
}

}