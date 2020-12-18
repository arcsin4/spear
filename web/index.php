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
    'get_running_status',
    'set_switch_off',
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
    $sql = "SELECT * FROM `crawl_result`
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
    $sql = "SELECT * FROM `website_list`
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
    $sql = "SELECT * FROM `event_keywords`
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

    $sql = "INSERT IGNORE INTO `event_keywords` SET `kw`=:kw ;";
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
    $sql = "DELETE FROM `event_keywords`
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


function set_switch_off()
{
    $rtn = array('result'=>'N');

    $conn = db();

    $sql = "INSERT INTO `running_status` SET `indicator`='run_switch',`content`='-1' ON DUPLICATE KEY UPDATE `content`=values(`content`) ;";
    $cmd = $conn->prepare($sql);

    if($cmd->execute())
    {
        $rtn = array('result'=>'Y');
    }

    show_result($rtn);
}


function get_running_status()
{
    $rtn = array('result'=>'Y', 'data'=>array());

    $conn = db();
    $sql = "SELECT * FROM `running_status`
        WHERE `indicator` <> 'run_switch' ";

    $cmd = $conn->prepare($sql);

    if ($cmd->execute()) {
        $res = $cmd->fetchAll();

        $start_time = 0;
        foreach($res as $value)
        {
            if($value['indicator'] == 'start_time'){
                $start_time = json_decode($value['content'], true);
            }
        }

        foreach($res as $value)
        {
            $k = $value['indicator'];
            $v = json_decode($value['content'], true);

            if($k == 'start_time'){
                $v = date('Y年m月d日 H:i:s', $v);
            }
            elseif($k == 'crawler_status'){
                $ws = self_get_websites();

                $vlist = array();
                foreach($v as $kk=>$vv){
                    $vv['website'] = $kk;
                    $vv['website_name'] = $kk;

                    if( in_array($kk,array_keys($ws))){
                        $vv['website_name'] = $ws[$kk];
                    }

                    $vv['freq'] = round((time() - $start_time)/$vv['run_counts'], 2);


                    foreach($vv['trigger_part'] as $tp_k=>$tp){
                        if($tp == 'title'){
                            $vv['trigger_part'][$tp_k] = '标题';
                        }
                        elseif($tp == 'content'){
                            $vv['trigger_part'][$tp_k] = '正文/摘要';
                        }
                    }

                    $vv['last_run'] = date('Y年m月d日 H:i:s', $vv['last_run']);
                    $vlist[] = $vv;
                }

                $v = $vlist;
            }
            elseif($k == 'env'){

                $vlist = array();
                foreach($v as $kk=>$vv){
                    $vv['key'] = $kk;

                    if( in_array($kk, array('default_crawl_freq', 'trigger_notify_period'))){
                        $vv['value'] = @$vv['value'][0].' ~ '.@$vv['value'][1];
                    }

                    $vlist[] = $vv;
                }

                $v = $vlist;
            }

            $rtn['data'][$k] = $v;
        }
    }

    show_result($rtn);
}
