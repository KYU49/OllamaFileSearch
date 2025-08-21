const evtSource = new EventSource('/your_sse_endpoint.php');

evtSource.addEventListener("search", (e) => {
	const data = JSON.parse(e.data);
	console.log("検索結果:", data.search_results);
});

evtSource.addEventListener("answer_token", (e) => {
	const data = JSON.parse(e.data);
	process.stdout.write(data.token); // トークンを順次表示
});

evtSource.addEventListener("end", () => {
	console.log("\nSSE終了");
	evtSource.close();
});