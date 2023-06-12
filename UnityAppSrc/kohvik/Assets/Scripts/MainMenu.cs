using System.Collections;
using TMPro;
using UnityEngine;
using UnityEngine.Networking;
using UnityEngine.SceneManagement;

public class MainMenu : MonoBehaviour
{
    [SerializeField] TMP_Text salesText;

    void Start()
    {
        StartCoroutine(GetSales());
    }

    private IEnumerator GetSales()
    {
        UnityWebRequest www = UnityWebRequest.Get($"{Constants.IP}/totalSales");
        yield return www.SendWebRequest();
        if (www.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(www.error);
        }
        else
        {
            string jsonResponse = www.downloadHandler.text.Trim();
            if (!jsonResponse.Contains("null")) {
                float number = float.Parse(jsonResponse[1..^1]);
                salesText.SetText(string.Format("{0:0.00}€", number / 100));
            }
            
        }
    }

    public void LoadCafe()
    {
        SceneManager.LoadScene("CashierScene");
    }

    public void LoadKitchen()
    {
        SceneManager.LoadScene("KitchenScene");
    }

    public void LoadTV()
    {
        SceneManager.LoadScene("OrderDisplay");
    }

    public void LoadMenu()
    {
        SceneManager.LoadScene("ItemMenu");
    }
}
