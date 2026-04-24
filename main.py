
           for centre in CENTRES:
                slots = fetch_slots(page, centre)
                if slots:
                    results[centre] = slots

                time.sleep(5)

            msg = format_msg(results)

            if msg and msg != last_msg:
                send_alert(msg)
                last_msg = msg

            time.sleep(CHECK_INTERVAL)

        except Exception as e:
            print("Error:", e)
            login(page)
 
