if __name__ == '__main__':
    port = check_port()
    ql_url = 'http://127.0.0.1:{0}/'.format(port)
    token = ql_login()
    s = requests.session()
    s.headers.update({"authorization": "Bearer " + str(token)})
    s.headers.update({"Content-Type": "application/json;charset=UTF-8"})
    ql_id = check_id()
    url_t = check_cloud()
    cloud_arg = cloud_info()
    update()
    ua = cloud_arg['User-Agent']
    wslist = get_wskey()
    envlist = get_env()

    processedCount = 0
    shortSleepTime = 60  # 每处理一个 JD_WSCK 后暂停 60 秒
    longSleepTime = 600  # 每累积处理 5 个 JD_WSCK 后暂停 600 秒

    for index, ws in enumerate(wslist):
        wspin = ws.split(";")[0]
        if "pin" in wspin:
            wspin = "pt_" + wspin + ";"
            return_serch = serch_ck(wspin)
            if return_serch[0]:
                jck = str(return_serch[1])
                if not check_ck(jck):
                    tryCount = 1
                    if "WSKEY_TRY_COUNT" in os.environ:
                        if os.environ["WSKEY_TRY_COUNT"].isdigit():
                            tryCount = int(os.environ["WSKEY_TRY_COUNT"])
                    for count in range(tryCount):
                        count += 1
                        return_ws = getToken(ws)
                        if return_ws[0]:
                            break
                        if count < tryCount:
                            logger.info("{0} 秒后重试，剩余次数：{1}\n".format(shortSleepTime, tryCount - count))
                            time.sleep(shortSleepTime)
                    if return_ws[0]:
                        nt_key = str(return_ws[1])
                        logger.info("wskey转换成功\n")
                        eid = return_serch[2]
                        ql_update(eid, nt_key)
                    else:
                        if "WSKEY_AUTO_DISABLE" in os.environ:
                            logger.info(str(wspin) + "账号失效\n")
                            text = "账号: {0} WsKey疑似失效".format(wspin)
                        else:
                            eid = return_serch[2]
                            logger.info(str(wspin) + "账号禁用\n")
                            ql_disable(eid)
                            text = "账号: {0} WsKey疑似失效, 已禁用Cookie".format(wspin)
                            ql_send(text)
                    
                    if (index + 1) % 5 == 0:  # 每处理5个 JD_WSCK 后暂停 600 秒
                        logger.info("累积处理 5 个 JD_WSCK，暂停 {0} 秒\n".format(longSleepTime))
                        time.sleep(longSleepTime)
                    else:
                        logger.info("暂停 {0} 秒\n".format(shortSleepTime))
                        time.sleep(shortSleepTime)
                else:
                    logger.info(str(wspin) + "账号有效\n")
                    eid = return_serch[2]
                    ql_enable(eid)
                    logger.info("--------------------\n")
            else:
                logger.info("\n新wskey\n")
                return_ws = getToken(ws)
                if return_ws[0]:
                    nt_key = str(return_ws[1])
                    logger.info("wskey转换成功\n")
                    ql_insert(nt_key)
                logger.info("暂停 {0} 秒\n".format(shortSleepTime))
                time.sleep(shortSleepTime)
        else:
            logger.info("WSKEY格式错误\n--------------------\n")

    logger.info("执行完成\n--------------------")
    sys.exit(0)
