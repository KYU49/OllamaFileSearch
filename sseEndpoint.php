<?php
// SSEヘッダー
header('Content-Type: text/event-stream');
header('Cache-Control: no-cache');
header('Connection: keep-alive');

// タイムアウト防止
set_time_limit(0);
ob_implicit_flush(true);
ob_end_flush();

$baseDir = __DIR__;
$pythonPath = $baseDir . "/py/.venv/Scripts/python.exe";

// POSTデータ取得
$input = json_decode(file_get_contents('php://input'), true);
$prompt = $input['prompt'] ?? '';

// Chroma検索を実行
$searchResults = shell_exec("{$pythonPath} {$baseDir}/py/search.py " . escapeshellarg($prompt));
$searchData = json_decode($searchResults, true) ?? [];

// 検索結果をSSEで送信
echo "event: search\n";
echo "data: " . json_encode(['search_results' => $searchData], JSON_UNESCAPED_UNICODE) . "\n\n";
ob_flush();
flush();

// LLM回答を生成
$cmd = "{$pythonPath} {$baseDir}/py/genAnswer.py " . escapeshellarg(json_encode($searchData)) . " " . escapeshellarg($prompt);
$process = popen($cmd, 'r');

if($process) {
	while (!feof($process)) {
		$line = fgets($process);
		if ($line !== false && trim($line) !== '') {
			// トークンを逐次送信
			echo "event: answer_token\n";
			echo "data: " . json_encode(['token' => trim($line)], JSON_UNESCAPED_UNICODE) . "\n\n";
			ob_flush();
			flush();
		}
	}
	pclose($process);
}

// 終了を通知
echo "event: end\n";
echo "data: {}\n\n";
flush();
?>