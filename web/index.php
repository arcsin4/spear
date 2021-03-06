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
    'search_trigger_msg',
    'set_switch_separately',
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

    return new PDO("mysql:host=127.0.0.1;dbname=sxy;port=3306;", 'sxy', 'Win171_!&!', $options_arr);
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
    $page = @$_REQUEST['page'];
    $limit = @$_REQUEST['limit'];

    if(@intval($page) <= 0){
        $page = 1;
    }
    else{
        $page = intval($page);
    }

    if(@intval($limit) <= 0){
        $limit = 30;
    }
    else{
        $limit = intval($limit);
    }

    $offset = ($page-1)*$limit;

    $conn = db();
    $sql_head = "SELECT * FROM `crawl_result`
        WHERE 1=1 ";
    $sql_head_count = "SELECT count(1) FROM `crawl_result`
        WHERE 1=1 ";

    $sql_stat = "";
    $sql = "";
    $sql_count = "";

    if(isset($websites) && is_array($websites) && count($websites)>0)
    {
        $sql_stat .= " AND website in ('0'";
        foreach($websites as $w){
            if(@$w != ""){
                $sql_stat .= ", ?";
            }
        }
        $sql_stat .= ")";
    }

    if(@$search_word != ""){
        $sql_stat .= " AND (title like ? or content like ?) ";
    }

    $sql = $sql_head.$sql_stat." ORDER BY news_time DESC, pid DESC LIMIT $limit OFFSET $offset";

    $sql_count = $sql_head_count.$sql_stat;

    $cmd = $conn->prepare($sql_count);

    $n = 1;
    if(isset($websites) && is_array($websites) && count($websites)>0)
    {
        foreach($websites as $w){
            if(@$w != ""){
                $cmd->bindValue($n, $w);
                $n = $n + 1;
            }
        }
    }

    if(@$search_word != ""){
        $cmd->bindValue($n, '%'.$search_word.'%');
        $n = $n + 1;
        $cmd->bindValue($n, '%'.$search_word.'%');
        $n = $n + 1;
    }

    if ($cmd->execute()) {
        $res_count = $cmd->fetchColumn();

        if($res_count <= 0){
            $rtn['code'] = 0;
            $rtn['msg'] = '';
            $rtn['count'] = 0;
            $rtn['data'] = array();

            show_result($rtn);
        }


        $rtn['code'] = 0;
        $rtn['msg'] = '';
        $rtn['count'] = intval($res_count);

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

        $cmd->execute();

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

function self_get_websites_all()
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
            $data[$v['website']] = $v;
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
        WHERE 1=1  ORDER BY website ASC ";

    $cmd = $conn->prepare($sql);

    $data = array();

    if ($cmd->execute()) {
        $res = $cmd->fetchAll();

        $ws = self_get_websites_all();

        $rtn = array(
            'all' => array('name'=>'全站点', 'kws'=>array(), 'separately'=>0),
        );

        foreach($ws as $k=>$v)
        {
            $rtn[$k] = array('name'=>$v['website_name'], 'kws'=>array(), 'separately'=>$v['separately_keywords']);
        }

        foreach($res as $k=>$v)
        {
            $website_name = $v['website'];

            if($v['website'] == ''){
                $rtn['all']['kws'][] = $v['kw'];
            }
            elseif( in_array($v['website'], array_keys($rtn))){
                $rtn[$v['website']]['kws'][] = $v['kw'];
            }
        }

        foreach($rtn as $k=>$v){
            if(@$k != 'all' && count($v['kws']) <= 0 && @$v['separately']=='0'){
                unset($rtn[$k]);
            }
        }

        $data = $rtn;
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
    $website = @$_REQUEST['select_website'];

    $rtn = array('result'=>'N');

    if(isset($kw_name) && @$kw_name != ""){
        //go on
    }
    else{
        show_result($rtn);
    }

    $conn = db();

    $sql = "INSERT IGNORE INTO `event_keywords` SET `kw`=:kw, `website`=:website ;";
    $cmd = $conn->prepare($sql);
    $cmd->bindValue(":kw", $kw_name);
    $cmd->bindValue(":website", $website);

    if($cmd->execute())
    {
        $rtn = array('result'=>'Y');
    }

    show_result($rtn);
}

function delete_keyword()
{

    $kw_arr = @$_REQUEST['keywords'];

    $rtn = array('result'=>'N');

    if(isset($kw_arr) && is_array($kw_arr) && count($kw_arr) > 0){
        //go on
    }
    else{
        show_result($rtn);
    }

    $conn = db();

    $sql = "DELETE FROM `event_keywords`
        WHERE kw=:kw AND website=:website ";

    foreach($kw_arr as $v){
        $tmp = explode("-", $v);

        if(@$tmp[0] == "all"){
            $tmp[0] = "";
        }

        $cmd = $conn->prepare($sql);
        $cmd->bindValue(":kw", @$tmp[1]);
        $cmd->bindValue(":website", @$tmp[0]);

        $cmd->execute();
    }

    $rtn = array('result'=>'Y');
    show_result($rtn);

}


function set_switch_separately()
{
    $website = @$_REQUEST['website'];
    $separately = @$_REQUEST['separately'];

    $rtn = array('result'=>'N');

    if(@$website != '' && in_array($separately,array('0','1'))){
        //go on
    }
    else{
        show_result($rtn);
    }

    $website = explode('-', $website);
    $website = $website[1];

    $conn = db();

    $sql = "UPDATE `website_list` SET separately_keywords=:separately
        WHERE website=:website ";

    $cmd = $conn->prepare($sql);
    $cmd->bindValue(":separately", @$separately);
    $cmd->bindValue(":website", @$website);


    if($cmd->execute())
    {
        $rtn = array('result'=>'Y');
    }
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

        $max_last_run = 0;

        foreach($res as $value)
        {
            $k = $value['indicator'];
            $v = json_decode($value['content'], true);

            if($k == 'start_time'){
                $v = date('m月d日 H:i:s', $v);
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

                    $vv['freq'] = $vv['run_counts']>0 ? round(($vv['last_run'] - $start_time)/$vv['run_counts'], 2) : 0;

                    foreach($vv['trigger_part'] as $tp_k=>$tp){
                        if($tp == 'title'){
                            $vv['trigger_part'][$tp_k] = '标题';
                        }
                        elseif($tp == 'content'){
                            $vv['trigger_part'][$tp_k] = '正文/摘要';
                        }
                    }

                    $vv['status'] = 'normal';
                    $vv['status_name'] = '正常';
                    if($vv['last_run'] <= 0){
                        $vv['status'] = 'error';
                        $vv['status_name'] = '异常（未运行/初次运行未结束）';
                    }
                    elseif((time() - $vv['last_run']) >= 600){
                        $vv['status'] = 'error';
                        $vv['status_name'] = '异常（'.self_calc_time(time() - $vv['last_run']).'未运行）';
                    }
                    elseif((time() - $vv['last_run']) >= 60){
                        $vv['status'] = 'warning';
                        $vv['status_name'] = '异常（'.self_calc_time(time() - $vv['last_run']).'未运行）';
                    }

                    $max_last_run = $vv['last_run'] > $max_last_run ? $vv['last_run'] : $max_last_run;

                    if($vv['last_run'] <= 0){
                        $vv['last_run'] = '--';
                    }
                    else{
                        $vv['last_run'] = date('m月d日 H:i:s', $vv['last_run']);
                    }

                    $vlist[] = $vv;
                }

                $v = $vlist;
            }
            elseif($k == 'event_keywords'){
                #{"all": ["TikTok", "\u533b\u7f8e", "\u534e\u4e3a", "\u6296\u97f3", "\u817e\u8baf", "\u8c37\u6b4c", "\u963f\u91cc", "\u7279\u65af\u62c9", "\u4eca\u65e5\u5934\u6761", "\u533b\u7597\u7f8e\u5bb9"], "36kr": ["TEST"], "thepaper": ["aaa", "TEST", "asdfaf"]}
                $ws = self_get_websites();

                $vlist = array();
                foreach($v as $kk=>$vv){

                    $website_name = $kk;

                    if($kk == '' || $kk == 'all'){
                        $website_name = '全站点';
                    }

                    if( in_array($kk,array_keys($ws))){
                        $website_name = $ws[$kk];
                    }

                    $vlist[$website_name] = $vv;
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

function self_calc_time($seconds){
    $rtn = "";
    if($seconds >= 86400){
        $rtn .= intval($seconds/86400)."天";
    }
    $seconds = $seconds%86400;

    if($seconds >= 3600){
        $rtn .= intval($seconds/3600)."小时";
    }
    $seconds = $seconds%3600;

    if($seconds >= 60){
        $rtn .= intval($seconds/60)."分";
    }
    $seconds = $seconds%60;

    if($seconds >= 0){
        $rtn .= intval($seconds)."秒";
    }

    return $rtn;
}


function search_trigger_msg()
{
    $rtn = array('result'=>'Y', 'data'=>array());

    $search_word = @$_REQUEST['search_word'];

    $conn = db();
    $sql = "SELECT * FROM `trigger_msg`
        WHERE 1=1 ";

    if(@$search_word != ""){
        $sql .= " AND trigger_words like ? ";
    }

    $sql .= " ORDER BY news_time DESC, pid DESC";

    $cmd = $conn->prepare($sql);

    $n = 1;
    if(@$search_word != ""){
        $cmd->bindValue($n, '%'.$search_word.'%');
        $n = $n + 1;
    }

    if ($cmd->execute()) {
        $rtn['data'] = $cmd->fetchAll();

        if(count($rtn['data']) > 0){

            $sql_updt = "UPDATE `trigger_msg` SET read_status=1 WHERE read_status=0 and news_time <= :news_time ";
            $cmd = $conn->prepare($sql_updt);
            $cmd->bindvalue(':news_time', $rtn['data'][0]['news_time']);

            $cmd->execute();
        }

        $res_ws = self_get_websites();

        foreach($rtn['data'] as $k=>$v)
        {
            $rtn['data'][$k]['popup'] = 0;
            if(date('H') >=9 && date('H') <=15 && $v['read_status'] == 0 && (time() - $v['news_time'])  <= 3600 ){
                $rtn['data'][$k]['popup'] = 1;
            }

            $rtn['data'][$k]['website_name'] = @$res_ws[$rtn['data'][$k]['website']] != "" ? $res_ws[$rtn['data'][$k]['website']] : $rtn['data'][$k]['website'];
            $rtn['data'][$k]['create_time'] = date('Y-m-d H:i:s', $v['create_time']);
            $rtn['data'][$k]['news_time'] = date('Y-m-d H:i:s', $v['news_time']);
        }

    }
    show_result($rtn);
}
