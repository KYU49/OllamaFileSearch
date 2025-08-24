document.onload = () => {
	const chatInput = document.getElementById("chatInput");
	const searchResultsDiv = document.getElementById("searchResults");
	const llmOutputDiv = document.getElementById("llmOutput");
	const titleSpan = document.getElementById("title");
	const backBtn = document.getElementById("backBtn");

	let originalResults = [];

	const searchBtn = document.getElementById("searchBtn");

	PHP_ADDRESS = "../sseEndpoint.php"

	function startSearch() {
		const prompt = chatInput.value.trim();
		if (!prompt) return;

		// 初期化
		searchResultsDiv.innerHTML = "";
		llmOutputDiv.innerHTML = "";
		titleSpan.textContent = "検索結果";
		backBtn.style.display = "inline-block";

		// SSE接続
		const evtSource = new EventSource(PHP_ADDRESS, { withCredentials: false });
		evtSource.addEventListener("search", (e) => {
			const data = JSON.parse(e.data);
			originalResults = data.search_results;
			renderSearchResults(originalResults);
		});

		evtSource.addEventListener("answer_token", (e) => {
			const data = JSON.parse(e.data);
			llmOutputDiv.textContent += data.token;
		});

		evtSource.addEventListener("end", () => {
			evtSource.close();
		});

		// PHPにPOST送信
		fetch(PHP_ADDRESS, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ prompt })
		});

		chatInput.value = "";
	}

	// Enterキーでも検索
	chatInput.addEventListener("keydown", (e) => {
		if (e.key === "Enter") startSearch();
	});
	// ボタンクリックでも検索
	searchBtn.addEventListener("click", startSearch);


	chatInput.addEventListener("keydown", async (e) => {
		if (e.key === "Enter") {
			const prompt = chatInput.value.trim();
			if (!prompt) return;

			// 初期化
			searchResultsDiv.innerHTML = "";
			llmOutputDiv.innerHTML = "";
			titleSpan.textContent = "検索結果";
			backBtn.style.display = "inline-block";

			// SSE接続
			const evtSource = new EventSource(PHP_ADDRESS, { withCredentials: false });
			evtSource.addEventListener("search", (e) => {
				const data = JSON.parse(e.data);
				originalResults = data.search_results;
				renderSearchResults(originalResults);
			});

			evtSource.addEventListener("answer_token", (e) => {
				const data = JSON.parse(e.data);
				llmOutputDiv.textContent += data.token;
			});

			evtSource.addEventListener("end", () => {
				evtSource.close();
			});

			// PHPにPOST送信
			fetch(PHP_ADDRESS, {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ prompt })
			});

			chatInput.value = "";
		}
	});

	backBtn.addEventListener("click", () => {
		titleSpan.textContent = "LangChain + Ollama Chat";
		backBtn.style.display = "none";
		searchResultsDiv.innerHTML = "";
		llmOutputDiv.innerHTML = "";
	});

	function renderSearchResults(results) {
		searchResultsDiv.innerHTML = "";

		// ラベルボタン
		const labels = [...new Set(results.map(r => r.metadata.label))];
		const labelContainer = document.createElement("div");
		labels.forEach(label => {
			const btn = document.createElement("span");
			btn.textContent = "#" + label;
			btn.className = "label-button";
			btn.addEventListener("click", () => {
				document.querySelectorAll(".label-button").forEach(b => b.classList.remove("active"));
				btn.classList.add("active");
				filterByLabel(label);
			});
			labelContainer.appendChild(btn);
		});
		searchResultsDiv.appendChild(labelContainer);

		// 検索結果リスト
		results.forEach(r => {
			const item = document.createElement("div");
			item.className = "result-item";
			item.dataset.label = r.metadata.label;
			item.innerHTML = `<strong>${r.metadata.source}</strong><br>${r.metadata.description}`;
			searchResultsDiv.appendChild(item);
		});
	}

	function filterByLabel(label) {
		document.querySelectorAll(".result-item").forEach(item => {
			item.classList.toggle("hidden", item.dataset.label !== label);
		});
	}
}