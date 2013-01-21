(ns nigel.matchers
  (:require [clojure.string :as s]))

(defn gif-matcher [speak msg]
  (when (re-find #".gif" msg)
    (speak "Another gif?")))

(def all-matchers [gif-matcher])
