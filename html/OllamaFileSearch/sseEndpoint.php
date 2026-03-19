<?php
// エラーログはApache + PHPなら`tail -f /var/log/apache2/error.log`

// SSEヘッダー
header('Content-Type: text/event-stream');
header('Cache-Control: no-cache');
header('Connection: keep-alive');
header('Access-Control-Allow-Origin: *');

// タイムアウト防止
set_time_limit(0);
// PHPの出力バッファを無効化
while (ob_get_level() > 0) {
    ob_end_flush();
}
ob_implicit_flush(true);

$baseDir = "/usr/local/lib/OllamaFileSearch";
$pythonPath = "/var/www/myapp/OllamaFileSearch";

chdir($pythonPath);

// --- 実行 (SSEストリーム開始) ---
echo "retry: 1000\n\n";	// 再接続までの待機ミリ秒
flush();

// POSTデータ取得
function escapeShellArgUtf8($arg) {
    // シングルクォートで囲み、内部のシングルクォートをエスケープ
    return "'" . str_replace("'", "'\\''", $arg) . "'";
}
$prompt = escapeShellArgUtf8(rawurldecode($_GET['prompt'] ?? ''));
// Chroma検索を実行
$searchResults = shell_exec("/opt/uv/uv run searchEndpoint.py " . $prompt);

// 検索結果をSSEで送信
echo "event: search\n";
echo "data: " . ($searchResults ?: "[]") . "\n\n";
flush();

// LLM回答を生成
$cmd = "/opt/uv/uv run genAnswerEndpoint.py " . $prompt;
// $cmd = "/opt/uv/uv run python3 -u genAnswerEndpoint.py " . $prompt . " 2>&1";
$process = popen($cmd, 'r');

if($process) {
	while (!feof($process)) {
		$line = fgets($process);
		$tline = trim($line);
		if ($line !== false && $tline !== '') {
			// トークンを逐次送信
			echo "event: answer_token\n";
			echo "data: " . rtrim($line) . "\n\n";
			flush();
		}
	}
	pclose($process);
}

/*if($process) {
    while (!feof($process)) {
        $line = fgets($process);
        $tline = trim($line);
        if ($line !== false && $tline !== '') {
            // デバッグ用：もしデータが [DONE] でも JSON でもない場合は、そのままエラーとして送る
            echo "event: answer_token\n";
            if (strpos($tline, '{') === 0 || $tline === "[DONE]") {
                echo "data: " . $tline . "\n\n";
            } else {
                // Python側で起きたエラー（Tracebackなど）をブラウザに流す
                echo "data: " . json_encode(["token" => "<div style='color:red'>Python Error: " . htmlspecialchars($tline) . "</div>"]) . "\n\n";
            }
            flush();
        }
    }
    pclose($process);
}*/


// 終了を通知
echo "event: end\n";
echo "data: {}\n\n";
flush();
?>