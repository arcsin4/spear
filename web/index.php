<?php

$action = @$_REQUEST['action'];

if(!isset($action) || @$action == ""){
    ob_clean();
    echo file_get_contents('index.html');
    exit();
}

$action_accept_arr = array(
    'search_crawl_result',
    'get_websites',
    'get_keywords',
    'create_keyword',
    'delete_keyword',
);

if (!in_array($action, $action_accept_arr) ){
    $rtn = array('result'=>'N');
    show_result($rtn);
}

$action();
exit();

function db() {
    $options_arr = array(
        PDO::MYSQL_ATTR_INIT_COMMAND => "SET NAMES utf8",
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC
    );

    return new PDO("mysql:host=127.0.0.1;dbname=sxy;port=3306;", 'root', 'root', $options_arr);
}

function show_result($rtn, $json_flag=true)
{
    #ob_clean();
    echo $json_flag == true ? json_encode($rtn) : $res;
    exit();
}

function search_crawl_result()
{
    $rtn = array('result'=>'Y', 'data'=>array());

    $websites = @$_REQUEST['websites'];
    $search_word = @$_REQUEST['search_word'];

    $conn = db();
    $sql = "SELECT * FROM `sxy`.`crawl_result`
        WHERE 1=1 ";

    if(isset($websites) && is_array($websites) && count($websites)>0)
    {
        $sql .= " AND website in ('0'";
        foreach($websites as $w){
            $sql .= ", ?";
        }
        $sql .= ")";
    }

    if(@$search_word != ""){
        $sql .= " AND (title like ? or content like ?) ";
    }

    $sql .= " ORDER BY news_time DESC, pid DESC ";

    $cmd = $conn->prepare($sql);

    $n = 1;
    if(isset($websites) && is_array($websites) && count($websites)>0)
    {
        foreach($websites as $w){
            $cmd->bindValue($n, $w);
            $n = $n + 1;
        }
    }

    if(@$search_word != ""){
        $cmd->bindValue($n, '%'.$search_word.'%');
        $n = $n + 1;
        $cmd->bindValue($n, '%'.$search_word.'%');
        $n = $n + 1;
    }

    if ($cmd->execute()) {
        $rtn['data'] = $cmd->fetchAll();

        $res_ws = self_get_websites();

        foreach($rtn['data'] as $k=>$v)
        {
            $rtn['data'][$k]['website_name'] = @$res_ws[$rtn['data'][$k]['website']] != "" ? $res_ws[$rtn['data'][$k]['website']] : $rtn['data'][$k]['website'];
            $rtn['data'][$k]['create_time'] = date('Y-m-d H:i:s', $v['create_time']);
            $rtn['data'][$k]['news_time'] = date('Y-m-d H:i:s', $v['news_time']);
        }

    }
    show_result($rtn);
}

function self_get_websites()
{
    $conn = db();
    $sql = "SELECT * FROM `sxy`.`website_list`
        WHERE 1=1 ORDER BY create_time DESC ";

    $cmd = $conn->prepare($sql);

    $data = array();

    if ($cmd->execute()) {
        $res = $cmd->fetchAll();

        foreach($res as $k=>$v)
        {
            $data[$v['website']] = $v['website_name'];
        }
    }

    return $data;
}

function get_websites()
{
    $rtn = array('result'=>'Y', 'data'=>array());

    $rtn['data'] = self_get_websites();
    show_result($rtn);
}

function self_get_keywords()
{
    $conn = db();
    $sql = "SELECT * FROM `sxy`.`event_keywords`
        WHERE 1=1 ";

    $cmd = $conn->prepare($sql);

    $data = array();

    if ($cmd->execute()) {
        $res = $cmd->fetchAll();

        foreach($res as $k=>$v)
        {
            $data[] = $v['kw'];
        }
    }

    return $data;
}

function get_keywords()
{
    $rtn = array('result'=>'Y', 'data'=>array());

    $rtn['data'] = self_get_keywords();
    show_result($rtn);
}


function create_keyword()
{
    $kw_name = @$_REQUEST['kw_name'];

    $rtn = array('result'=>'N');

    if(isset($kw_name) && @$kw_name != ""){
        //go on
    }
    else{
        show_result($rtn);
    }

    $conn = db();

    $sql = "INSERT IGNORE INTO `sxy`.`event_keywords` SET `kw`=:kw ;";
    $cmd = $conn->prepare($sql);
    $cmd->bindValue(":kw", $kw_name);

    if($cmd->execute())
    {
        $rtn = array('result'=>'Y');
    }

    show_result($rtn);
}

function delete_keyword()
{

    $keywords = @$_REQUEST['keywords'];

    $rtn = array('result'=>'N');

    if(isset($keywords) && is_array($keywords) && count($keywords) > 0){
        //go on
    }
    else{
        show_result($rtn);
    }

    $rtn = array('result'=>'Y');

    $conn = db();
    $sql = "DELETE FROM `sxy`.`event_keywords`
        WHERE kw in ('' ";

    foreach($keywords as $w){
        $sql .= ", ?";
    }
    $sql .= ")";

    $cmd = $conn->prepare($sql);

    $n = 1;
    foreach($keywords as $w){
        $cmd->bindValue($n, $w);
        $n = $n + 1;
    }

    $cmd->execute();

    show_result($rtn);

}
