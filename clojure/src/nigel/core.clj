(ns nigel.core
  (:require [clojure.string :as s])
  (:use [nigel.matchers :only [all-matchers]])
  (:import (java.net Socket)
           (java.io PrintWriter InputStreamReader BufferedReader)))

(def irc-config
  (atom nil))

(declare conn-handler)

(defn connect [conf]
  (let [socket (Socket. (:host conf) (:port conf))
        in (BufferedReader. (InputStreamReader. (.getInputStream socket)))
        out (PrintWriter. (.getOutputStream socket))
        conn (ref {:in in :out out})]
    (doto (Thread. #(conn-handler conn)) (.start))
    conn))

(defn write [conn msg]
  (doto (:out @conn)
    (.println (str msg "\r"))
    (.flush)))

(defn parse-message [msg] 
  "Return what a person said or nil"
  (let [parts (s/split msg #" :")]
    (if (< 2 (count parts))
      nil
      (s/join ":" (rest parts)))))

(defn respond [conn message]
  (let [msg (str ":abc PRIVMSG " (:room @irc-config) " :" message)]
    (write conn msg)))

(defn react [conn message]
  (let [msg (parse-message message)
        speak (partial respond conn)]
    (when msg
      (dorun
        (map #(% speak msg) all-matchers)))))

(defn conn-handler [conn]
  (while (nil? (:exit @conn))
    (let [msg (.readLine (:in @conn))]
      (println msg)
      (cond 
       (re-find #"^ERROR :Closing Link:" msg) 
       (dosync (alter conn merge {:exit true}))
       (re-find #"^PING" msg)
       (write conn (str "PONG "  (re-find #":.*" msg)))
       :else (react conn msg)))))

(defn login [conn conf]
  (write conn (str "NICK " (:nick conf)))
  (write conn (str "USER " (:nick conf) " 0 * :" (:name conf)))
  (write conn (str "JOIN " (:room conf))))

(defn -main
  [& args]
  (reset! irc-config (load-file (or (first args) "config.clj")))
  (let [irc (connect @irc-config)]
    (login irc @irc-config)))
